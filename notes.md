# Network debugging notes

**pScheduler**

```
/usr/lib/perfsonar/scripts/mod_interface_route --command add --device wired_dev_name --ipv4_gateway gateway_ip
```

**Connecting to Wireless**

```
pSSID uses wpa_supplicant to connect to wireless

There are different wpa_supplicant files for each ssid

These files are stored in /etc/wpa_supplicant/
In the format wpa_supplicant_ssid.conf
```

**Create wpa supplicant**

```
Copy over template file
Edit new configuration file with login info

cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant_ssid.conf
```

**Hash password**
```
echo -n plaintext_password_here | iconv -t utf16le | openssl md4

This password can replace password field in wpa_supplicant with the hash prefix

password=hash:hashed_password
```

**Test pScheduler**
```
pscheduler ping ip_wireless_interface
pscheduler ping ip_wired_interface

Should come back quickly saying pscheduler is alive
```

**pScheduler over the wire**
```
pscheduler task --bind wire_ip \
throughput --source wire_ip \
--dest throughput_server
```

**Routes**
```
When the pi comes up the wired interface will have the default route
This should be removed by the connect_bssid code
It will then bring up a default route over the wireless interface for testing

There should be routes to the gateway for the bastion and the ELK Server

Static routes can be added in the netplan yaml file
/etc/netplan/50-cloud-init.yaml

Or manually using ip route add
```
