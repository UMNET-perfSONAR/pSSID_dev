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

