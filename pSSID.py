from parse_config import Parse, tests
from schedule import Schedule
import argparse
import daemon
import sys
import time
import datetime
from dateutil.tz import tzlocal
import myapi



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


while True:
    print
    next_task = schedule.get_queue[0] 
    schedule.pop(next_task) 
    print("Next Task: ")

    
    pSSID_spec = next_task.argument[0]
    task_name = next_task.argument[1]
    task_ssid = next_task.argument[2]
    task_cron = next_task.argument[3]

    print_task = time.ctime(next_task.time) + \
        " SSID: " + next_task.argument[2]["name"] + \
        " Test: " + next_task.argument[1]

    print (print_task)

    now = time.time()
    sleep_time = next_task.time - now if next_task.time > now else 0
    print("Waiting: ", sleep_time)
    time.sleep(sleep_time)
    print("Result URL: ")
    

    pSched_task = pSSID_spec["TASK"]

   


    #this will run one test for particular SSID
    myapi.main(pSched_task)
    ##this does not return anything but can be modified
    ##myapi syslogs the result url


    schedule.reschedule(pSSID_spec, task_ssid, task_cron)
    print("NEW QUEUE:")
    schedule.print_queue()


    if schedule.empty():
        print("ERROR: this should never reach")




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

#   next task - current time = sleep until SSID test time

# here it is time to execute a task

# scan task SSID for component BSSID
# use file ssid_scan.py
# ssid_scan.py sub main function will print out list of all BSSIDs for each SSID in the config
# signal strength, BSSID name, etc.

# foreach ( BSSID in SSID ) {
        # decide if we connect to this BSSID
        # min_signal per SSID

        # connect to the BSSID with given Credentials / Mechanism
        #   - gather connection data/metadata
        #  use file connect_bssid.py
        #  connect_bbsid.py sub-main will connect to given BSSID
        #  "by hand" use ssid_scan.py for list of BSSIDs, feed that to connect_bbsid.py

        # foreach ( TEST in BSSID TASK LIST ) {
        #   run test with pScheduler
        #  talk to pScheduler with rest.py
        #  rest.py sub-main takes test spec runs it against localhost pscheduler
        #  receive a result then archive results with connection metadata
        #  1. receive result from pscheduler
        #  2. add connection metadata to result JSON
        #  3. send "complete" result to archiver
        #  To do step three: extra file archive.py
        #  archive.py has a sub-main that sends a given JSON result to an archiver
        }

        # log off BSSID (if that's a thing)
    }
    # requeue SSID with schedule.py
}

