"""
Implement ssid scanner with the wifi library
Uses iwlist and must be run as root
"""

from wifi import Cell, Scheme
import json
import logging
from logging.handlers import SysLogHandler
import time

# Create logger
pSSID_logger = logging.getLogger('scan_logger')
pSSID_logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = '/dev/log', facility='local3')
pSSID_logger.addHandler(handler)


def get_all_bssids(interface):
    """
    Scan the given interface for all bssids
    Return a list of json objects representing all bssids
    """
    start_time = time.time()
    cells = Cell.all(interface) # Specify interface to scan on

    wifi_list = []
    for cell in cells:
        bssid = {}
        bssid['ssid'] = cell.ssid
        bssid['signal'] = cell.signal
        bssid['address'] = cell.address
        bssid['frequency'] = cell.frequency
        bssid['quality'] = cell.quality
        bssid['bitrates'] = cell.bitrates
        bssid['encrypted'] = cell.encrypted
        bssid['channel'] = cell.channel
        bssid['mode'] = cell.mode
        bssid = json.dumps(bssid)
        wifi_list.append(bssid)

    end_time = time.time()
    elapsed_time = end_time - start_time
    log_msg = "Scan finished in " + str(elapsed_time)
    pSSID_logger.info(log_msg)

    return wifi_list


def print_ssid(interface, ssid):
    """
    Scan on the given interface
    Return a list of all bssids with the given ssid
    """
    start_time = time.time()
    all_bssids = get_all_bssids(interface)
    ssid_list = []

    # Check complete list for matching ssids
    for bssid in all_bssids:
        bssid = json.loads(bssid)
        if bssid['ssid'] == ssid:
            ssid_list.append(bssid)

    for entry in ssid_list:
        print(entry)

    end_time = time.time()
    elapsed_time = end_time - start_time
    log_msg = "Scan finished in " + str(elapsed_time)
    pSSID_logger.info(log_msg)

