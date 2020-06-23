from parse_config import Parse, tests
from schedule import Schedule
import argparse
import daemon
import sys
import time
import datetime
from dateutil.tz import tzlocal
import myapi

def single_BSSID_qualify(bssid, ssid):
    """
    Take in a json object representing a bssid
    Return True if criteria is met
    """
    ret = True
    bssid = json.loads(bssid)

    # Disqualify based on ssid
    if bssid['ssid'] != ssid['name']:
        ret = False
    #   if jimmy wants us to report "rougue" SSIDs
    #       send rougue warning

    # Disqualify based on signal strength
    if bssid['signal'] < ssid['min_signal']:
        ret = False
    
    # Disqualify based on channel
    # if bssid['channel'] isn't in the SSID channel list
    #    if ( we're supposed to warn about channel mismatches )
    #        warn about the channel mismatch
    #    if ( we're supposed to not connect to mismatched channels )
    #        ret = False

    return ret



def BSSID_qualify(bssid_list, ssid):
    """
    Take in a list of all bssids
    Returns the number of valid bssids according to the input values
    """
    qualified_bssids = 0

    for bssid in bssid_list:
        if single_BSSID_qualify(bssid, ssid):
            qualified_bssids += 1

    return qualified_bssids


# def run_task(bssid_list, ssid, min_signal, interface):
#     """
#     Run a task given a list of possible bssids
#     """
#     for bssid in bssid_list:
#         if single_BSSID_qualify(bssid, ssid, min_signal):
#             bssid = json.loads(bssid)
#             # Connect to bssid
#             connect_bssid.prepare_connection(bssid['ssid'], bssid['address'], \
#                     interface)


def debug(parsed_file, schedule):    
    #print parsed objects
    tests(parsed_file)
    #send first runs schedule to syslog    
    schedule.initial_schedule()
    schedule.print_queue()


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
schedule.initial_print()
print


if args.debug:
    with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, 
        working_directory='/home/vagrant'):
        debug(parsed_file, schedule)
        exit(0)


# loop forever () {
def loop_forever():
    global child_exited
    pid_child = 0
    scan_expire = 0
    signal_cutoff = -75
    scan_interval = 300
    task_ttl = 30
    interface = "wlan0"
    computed_TTL = 0

    ssid_table = ssid_scan.get_all_bssids('wlan0')
    scan_expire = time.time() + scan_interval
    # foreach defined SSID
    #     if ( we have too few BSSIDs that qualify )
    #         warning

    next_task = schedule.get_queue[0] 
    schedule.pop(next_task)
    pSSID_spec, task_name, task_ssid, task_cron = retrieve(next_task)

    print("Next Task: ")
    print_task = time.ctime(next_task.time) + \
        " SSID: " + task_ssid["name"] + \
        " Test: " + task_name
    print (print_task)

    while True:        

        if pid_child != 0:
            signal.signal(signal.SIGCHLD, sigh)

            time.sleep(computed_TTL) #will wait after ttl established

        elif next_task.time > time.time():
            #next task - current time = sleep until SSID test time
            sleep_time = next_task.time - time.time() 
            print("Waiting: ", sleep_time)
            time.sleep(sleep_time) 



        # if(rabbitmq):
        #     message = ...
        #     #
        #     #
        #     continue

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
            schedule.reschedule(pSSID_spec, task_ssid, task_cron)
            print("NEW QUEUE:")
            schedule.print_queue()

            next_task = schedule.get_queue[0] 
            schedule.pop(next_task)
            pSSID_spec, task_name, task_ssid, task_cron = retrieve(next_task)

            if schedule.empty():
                print("ERROR: this should never reach")

            continue


        # Check if table is expired
        if scan_expire < time.time():
            # Rescan for bssids
            ssid_table = ssid_scan.get_all_bssids('wlan0')
            scan_expire = time.time() + scan_interval


        num_bssids = BSSID_qualify(ssid_table, task_ssid) 

        # Compute task time to live
        if num_bssids:
            computed_TTL = num_bssids * task_ttl
        else:
            continue



        pid_child = os.fork()

        if pid_child == 0:
            print("CHILD")

            for bssid in ssid_table:
                print("BSSID switch")
                if single_BSSID_qualify(bssid, task_ssid):
                    bssid = json.loads(bssid)
                    # Connect to bssid
                    connect_bssid.prepare_connection(bssid['ssid'], bssid['address'], \
                            interface)

                    pSSID_spec["TASK"]["archives"] = transform(pSSID_spec,task_name, bssid)
                    pSched_task = pSSID_spec["TASK"]

                    rest_api.main(pSched_task)


            exit(0)
        

        



with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr):
    loop_forever()




# read config file
# call function in parse_config.py
# parse_config.py sub-main will validate that the config file is correct

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

# loop forever () {

#  # compute sleep time
#  if ( interface_in_use == True ) {
#    # sleep forever
#    sleep_time = -1
#  } else {
#    if ( task.scheduled_time < current_time ) {
#       # run a task immediately (underwater)
#       sleep_time = 0;
#    } else {
#       sleep_time = task.scheduled_time - current_time;
#    } 
#  }
#  

# if sleep_time == -1, that means sleep_forever
# sleep( sleep_time )
# if ( pid_child != 0 ) {
#    os.waitpid( child, sleep_time );
# else 
#    sleep( sleep_time )

# if ( finished_tasks ) {  # signals
#    cleanup_finished_tasks();
#      - interface_in_use = False
#      - requeue task
#      - pid_child = 0;
#    continue;
# }

# here it is time to execute a task
#    execute_task( TASK );
#      - existing other process that will signal when it's done
#      - interface_in_use = True
#      - pid_child  = child's pid
# 
#    requeue_task( TASK );


# requeue SSID with schedule.py
#}

