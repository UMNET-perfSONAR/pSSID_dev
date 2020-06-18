import connect_bssid
import ssid_scan
import time
import json


# Minimum signal strength to connect
# Greater numbers are stronger
signal_cutoff = -75
scan_interval = 300
task_ttl = 10


def single_BSSID_qualify(bssid, ssids, min_signal):
    """
    Take in a json object representing a bssid
    Return True if criteria is met
    """
    bssid = json.loads(bssid)

    # Disqualify based on ssid
    if bssid['ssid'] not in ssids:
        return False

    # Disqualify based on signal strength
    if bssid['signal'] < min_signal:
        return False

    return True


def BSSID_qualify(bssid_list, ssids, min_signal):
    """
    Take in a list of all bssids
    Returns the number of valid bssids according to the input values
    """
    qualified_bssids = 0

    for bssid in bssid_list:
        if single_BSSID_qualify(bssid, ssids, min_signal):
            qualified_bssids += 1

    return qualified_bssids


def run_task(bssid_list, ssids, min_signal, interface):
    """
    Run a task given a list of possible bssids
    """
    for bssid in bssid_list:
        if single_BSSID_qualify(bssid, ssids, min_signal):
            bssid = json.loads(bssid)
            # Connect to bssid
            connect_bssid.prepare_connection(bssid['ssid'], bssid['address'], \
                    interface)
            # Run task
            print(bssid['ssid'])
            exit(1)


def main(task_ssids):
    """
    Take in a list of ssids
    Fill table with all bssids
    Connect to those with good singal strength
    """

    # Fill table and set init start time
    ssid_table = ssid_scan.get_all_bssids('wlan0')
    scan_expire = time.time() + scan_interval

    # Loop to simulate daemon
    while True:

        # Check if table is expired
        if scan_expire < time.time():
            # Rescan for bssids
            ssid_table = ssid_scan.get_all_bssids('wlan0')
            scan_expire = time.time() + scan_interval

        num_bssids = BSSID_qualify(ssid_table, task_ssids, signal_cutoff)

        # Compute task time to live
        if num_bssids:
            computed_TTL = num_bssids * task_ttl
        else:
            continue

        print(computed_TTL)

        # Fork child
        run_task(ssid_table, task_ssids, signal_cutoff, 'wlan0')



# Bring up table of all below ssids
# Connect to all and ran task
main(['MWireless'])
