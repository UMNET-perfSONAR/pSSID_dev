from parse_config import Parse, tests
from schedule import Schedule
import argparse
import daemon
import sys
import time
import datetime
import rest_api
import psjson
import os
import signal
import ssid_scan
import connect_bssid
import json
import warnings
import pika



child_exited = False

def sigh(signum, frame):
    global child_exited
    if signum == signal.SIGTERM:
        exit(1) 

    if signum == signal.SIGCHLD:
        (pid, status) = os.waitpid(-1, 0) 
        print ("(SIGCHLD) child exited with status: " + str(os.WEXITSTATUS(status)), pid)
        child_exited = True


def print_bssid(diagnostic, bssid):
    print(" ")
    print(diagnostic)
    print(bssid)

def single_BSSID_qualify(bssid, ssid = {}, ssid_list=[], unknown_SSID_warn = True, scan = False, rogue_list =[]):
    """
    Take in a json object representing a bssid
    Return True if criteria is met

    ssid is a single SSID_profiles object
    """
    ret = True
    bssid = json.loads(bssid)
    rogue_ssid = True

    if scan:
        for i in ssid_list:
            # for scan check if matches any other ssid
            if bssid["ssid"] == i["SSID"]:
                rogue_ssid = False
                ssid = i
                break


        if rogue_ssid:
            ret = False
            if bssid['ssid'] not in rogue_list:
                rogue_list.append(bssid['ssid'])
                if unknown_SSID_warn:
                    diagn = "Rogue SSID: " + bssid['ssid']
                    #print(diagn, bssid)
                rogue_ssid = True

    elif bssid["ssid"] != ssid["SSID"]:
            ret = False         
    else:
        rogue_ssid = False
    

    # Disqualify based on channel
    if not rogue_ssid and bssid["channel"] not in ssid["channels"]: 
        if ssid["channel_mismatch_warning"]:
            diagn = "channel mismatch: for SSID " + ssid["SSID"] + " " + str(ssid["channels"])
            #print(diagn, bssid)
        if not ssid["channel_mismatch_connect"]:
            ret = False

    # Disqualify based on signal strength
    elif not rogue_ssid and bssid["signal"] < ssid["min_signal"]:
        #print("SSID " + ssid["SSID"] + " low signal: ", bssid["signal"], " < ", ssid["min_signal"] )
        ret = False



    return ret, ssid
        





def BSSID_qualify(bssid_list, ssid = {}, ssid_list=[],  unknown_SSID_warn = True, scan = False):
    """
    Take in a list of all bssids
    Returns the number of valid bssids according to the input values

    ssid is a single SSID_profiles object
    """
    qualified_bssids = 0
    rogue_list = []
    qualified_per_ssid = {}

    if scan:
        for i in ssid_list:
            qualified_per_ssid[i["SSID"]] = 0

    for bssid in bssid_list:
        ret, ssid  = single_BSSID_qualify(bssid, ssid, ssid_list, unknown_SSID_warn, scan, rogue_list)
        if ret:            
            qualified_bssids += 1
            if scan:
                qualified_per_ssid[ssid["SSID"]] += 1

    if scan:
        for j in ssid_list:
            if qualified_per_ssid[j["SSID"]] < j["min_qualifying"]:
                print("Too few qualified_bssids for", j["SSID"])


    return qualified_bssids



def transform(main_obj, bssid):
    transform = {}
    transform["time"] = time.ctime(time.time())
    transform["SSID"] = bssid["ssid"]
    transform["BSSID"] = bssid["address"]
    transform["ESSID"] = bssid["ssid"]
    #transform["AP"] = task_ap
    transform["task"] = main_obj["name"]
    transform["signal"] = bssid["signal"]
    transform["frequency"] = bssid["frequency"]


    script_str = psjson.json_dump(transform)
    insert = ", \\(.)"
    script_str = script_str.replace("\"", "\\\"")
    script_str = script_str.rstrip("}")
    script_str ="\""+ script_str + insert + "}\""

    append = "\"\\\"succeeded\\\": \\(.result.succeeded), \" + if (.result.succeeded) then \"\\\"result\\\": \\(.result)\" else \"\\\"error\\\":\\\"err\\\"\" end | "

    #list
    archives_list = main_obj["TASK"]["archives"]
    new_list = []
    for i in archives_list:
        i["transform"] = {}
        i["transform"]["script"] = append + script_str
        new_list.append(i)
        #print(i)

    #print(script_str)

    return new_list


def debug(parsed_file, schedule):    
    #print parsed objects
    tests(parsed_file)
    #send first runs schedule to syslog    
    schedule.initial_schedule()
    schedule.print_queue()


def retrieve(next_task):
    return next_task.argument[0], \
        next_task.argument[1], \
        next_task.argument[2], \
        next_task.argument[3]


parser = argparse.ArgumentParser(description='pSSID')
parser.add_argument('file', action='store',
  help='json file')
parser.add_argument('--debug', action='store_true',
  help='sanity check')
args = parser.parse_args()


# read config file
# call function in parse_config.py
# parse_config.py sub-main will validate that the config file is correct
config_file = open(args.file, "r")
parsed_file = Parse(config_file)
config_file.close()



# get resources

# daemonize - this belongs in master main

# daemonize

# queue strategy
# foreach task
#  schedule it at the appropriate time
#  use schedule.py
#  schedule.py sub-main will take a config and by default print the next occurance
# of each task.  Should also include an optional time duration, if so, print the schedule
# for the given duration

schedule = Schedule(parsed_file)
#initial queue
schedule.initial_schedule()
#schedule.initial_print()
#print


if args.debug:
    with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, 
        working_directory=os.getcwd()):
        debug(parsed_file, schedule)
        exit(0)


# loop forever () {
def loop_forever():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel=connection.channel()
    channel.exchange_declare(exchange='logs', exchange_type='direct')
    result=channel.queue_declare(queue='',exclusive=True)
    channel.queue_bind(exchange='logs', queue=result.method.queue, routing_key='pi-point')
    
    global child_exited
    pid_child = 0
    task_ttl = 30
    computed_TTL = 10

    #interface would depend
    interface = {}
    scanned_table = []
    bssid_list = {}

    next_task = schedule.get_queue[0] 
    schedule.pop(next_task)
    main_obj, cron, ssid, scan = retrieve(next_task)

    print("Next Task: ")
    print_task = time.ctime(next_task.time) + \
        " main_obj: " + main_obj["name"]
    print (print_task)

    while True: 

        if scan:
            if next_task.time > time.time():
                sleep_time = next_task.time - time.time()
                print("Waiting: ", sleep_time)
                time.sleep(sleep_time) 

            
            ssid_list = main_obj["profiles"]

            scanned_table = ssid_scan.get_all_bssids(main_obj["interface"])

            #print("ssid_list", ssid_list)

            BSSID_qualify(scanned_table, ssid_list =ssid_list,  unknown_SSID_warn =main_obj["unknown_SSID_warning"], scan=True)


            bssid_list[main_obj["name"]] = scanned_table
            interface[main_obj["name"]] = main_obj["interface"]

            schedule.reschedule(main_obj,cron, ssid, scan=True)

            next_task = schedule.get_queue[0] 
            schedule.pop(next_task)
            main_obj, cron, ssid, scan = retrieve(next_task)

            print("Next Task: ")
            print_task = time.ctime(next_task.time) + \
                " main_obj: " + main_obj["name"]
            print (print_task)

            continue

        if pid_child != 0:
            signal.signal(signal.SIGCHLD, sigh)

            for msg in channel.consume('', inactivity_timeout = computed_TTL):
                if msg!=None:
                    method, properties, body = msg
                    print (body)
                    break

            #time.sleep(computed_TTL) #will wait after ttl established

        elif next_task.time > time.time():
            sleep_time = next_task.time - time.time() 
            print("Waiting: ", sleep_time)

            for msg in channel.consume('', inactivity_timeout = sleep_time):
                if msg!=None:
                    method, properties, body = msg
                    print (body)
                    break

            #time.sleep(sleep_time) 
   
      
        if(pid_child != 0):            
            if not child_exited:
                print ("***kill child***", pid_child)
                os.kill(pid_child, signal.SIGKILL)          
                try:
                    os.wait()
                except:
                    print("CHILD DEAD")
            else:
                child_exited = False
                # requeue SSID with schedule.py

            pid_child = 0
            schedule.reschedule(main_obj, cron, ssid)
            print("NEW QUEUE:")
            schedule.print_queue()

            next_task = schedule.get_queue[0] 
            schedule.pop(next_task)
            main_obj, cron, ssid, scan = retrieve(next_task)

            if schedule.empty():
                print("ERROR: this should never reach")

            continue


        
        num_bssids = BSSID_qualify(scanned_table, ssid) 

        # Compute task time to live
        if num_bssids:
            computed_TTL = num_bssids * task_ttl
        else:
            continue



        pid_child = os.fork()

        if pid_child == 0:
            print("CHILD")

            for bssid in bssid_list[main_obj["BSSIDs"]]:
                print("BSSID switch")
                ret, retssid = single_BSSID_qualify(bssid, ssid)
                if ret:
                    bssid = json.loads(bssid)
                    # Connect to bssid
                    connect_bssid.prepare_connection(bssid['ssid'], bssid['address'], interface[main_obj["BSSIDs"]])

                    main_obj["TASK"]["archives"] = transform(main_obj, bssid)
                    pSched_task = main_obj["TASK"]

                    rest_api.main(pSched_task)


            exit(0)
        

        



with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr):
    loop_forever()
