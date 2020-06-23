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
    bssid = json.loads(bssid)

    # Disqualify based on ssid
    if bssid['ssid'] != ssid['name']:
        return False

    # Disqualify based on signal strength
    if bssid['signal'] < ssid['min_signal']:
        return False

    return True



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

