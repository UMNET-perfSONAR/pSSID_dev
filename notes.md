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

cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant_ssid.conf
```

**Hash password**
```
echo -n plaintext_password_here | iconv -t utf16le | openssl md4

This password can replace password field in wpa_supplicant with the hash prefix

password=hash:hashed_password
```
