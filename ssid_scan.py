"""
Implement ssid scanner with the wifi library
Uses iwlist and must be run as root
"""

from wifi import Cell, Scheme

# Scan network for all visible BSSIDs
# Return a list of ('SSID', 'Mac Address', 'Signal Strength', 'Frequency')

def get_all_bssids(interface):
    cells = Cell.all(interface) # Specify interface to scan on

    wifi_list = []
    for cell in cells:
        wifi_list.append((cell.ssid, cell.address, cell.signal, cell.frequency))
    return wifi_list


# Given a config containing SSIDs
# List all BSSIDs under those SSIDs

def ssid_scan(ssid, interface):
    valid_bssids = []

    # Get all BSSIDs
    con_list = get_all_bssids(interface)
    for bssid in con_list:
        # Check for valid BSSIDs
        if bssid[0] == ssid:
            valid_bssids.append(bssid)

    return valid_bssids


# Display all visible BSSIDs
def display_all():
    for bssid in get_all_bssids('wlan0'):
        print(bssid)
