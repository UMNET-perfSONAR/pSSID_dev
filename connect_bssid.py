"""
Connect to an input SSID on an input BSSID
"""

import json
import shutil
import time
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C

DEBUG = False


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        if DEBUG:
            print(json.dumps({host.name: result._result}, indent=4))


def prepare_connection(ssid, bssid, interface, auth):
    """
    Prepare a connection to a given ssid and bssid using wpa_supplicant
    Configure and connect on given interface
    Decide connect method and config file based on auth
    """
    start_time = time.time()

    # Determine auth method
    if auth['type'] == 'MacAddress':
        print('Connect to MSetup')
        exit()

    elif auth['type'] == 'User':
        wpa_supp_path = '/etc/wpa_supplicant/wpa_supplicant_' + ssid + '.conf'
        print('User auth')

    # Format SSID and BSSID for wpa supplicant
    ssid_line = '    ssid="' + ssid + '"'
    bssid_line = '    bssid=' + bssid 

    # Add interface to ip commands
    bring_down = ('ip link set ' + interface + ' down')
    flush_config = ('ip addr flush dev ' + interface)
    bring_up = ('ip link set ' + interface + ' up')

    # Add interface to wpa supplicant and dhclient commands
    run_wpa_supplicant = ('wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant.conf -i ' + interface)
    dhclient = ('dhclient ' + interface)

    # since the API is constructed for CLI it expects certain options to always be set in the context object
    context.CLIARGS = ImmutableDict(connection='local', module_path=['/to/mymodules'], forks=10, become=None, become_method=None, become_user=None, check=False, diff=False)

    # initialize needed objects
    loader = DataLoader() # Takes care of finding and reading yaml, json and ini files
    passwords = dict(vault_pass='secret')

    # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
    results_callback = ResultCallback()

    # create inventory, use path to host config file as source or hosts in a comma separated string
    inventory = InventoryManager(loader=loader, sources='localhost,')

    # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # Playbook to connect to a bssid
    play_source =  dict(
            name = "Ansible Play",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = [

                # Check for wpa_supplicant file
                dict(action=dict(module='start', path=wpa_supp_path), register='wpa_exists'),

                # Exit play if wpa_supplicant is not found
                dict(action=dict(module='debug', msg='Could not find wpa_supplicant with given ssid'), when='not wpa_exists.stat.exists'),
                dict(action=dict(module='meta', args='end_play'), when='not wpa_exists.stat.exists'),

                # Remove default route to make dhclient happy
                dict(action=dict(module='command', args='ip route del default'), ignore_errors='yes'),

                # Remove WiFi interface config
                dict(action=dict(module='file', path='/var/run/wpa_supplicant/wlan0', state='absent')),

                # Kill wpa_supplicant
                dict(action=dict(module='command', args='killall wpa_supplicant'), ignore_errors='yes'),

                # Bring WiFi interface down
                dict(action=dict(module='command', args= bring_down)),

                # Flush WiFi interface config
                dict(action=dict(module='command', args=flush_config)),

                # Bring interface back up
                dict(action=dict(module='command', args= bring_up)),

                # Add SSID to wpa_supplicant
                dict(action=dict(module='lineinfile', path=wpa_supp_path, regexp='^(.*)ssid=(.*)$', line=ssid_line)),

                # Add BSSID to wpa_supplicant
                dict(action=dict(module='lineinfile', path=wpa_supp_path, regexp='^(.*)bssid=(.*)$', line=bssid_line)),

                # Connect to WiFi
                dict(action=dict(module='command', args=run_wpa_supplicant)),

                # Get an IP
                dict(action=dict(module='command', args=dhclient)),

                # Restart resolver
                dict(action=dict(module='systemd', state='restarted', name='systemd-resolved'))
             ]
        )

    # Create the playbook
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # Run the playbook
    tqm = None
    try:
        tqm = TaskQueueManager(
                  inventory=inventory,
                  variable_manager=variable_manager,
                  loader=loader,
                  passwords=passwords,
                  stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
              )
        result = tqm.run(play) # most interesting data for a play is actually sent to the callback's methods
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    connection_info = {}
    connection_info['ssid'] = ssid
    connection_info['bssid'] = bssid
    connection_info['time'] = elapsed_time
    json_info = json.dumps(connection_info)

