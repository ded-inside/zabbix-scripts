# -*- coding: utf-8 -*-
import sys
import requests
import json
import time
url = "*YOUR ZABBIX URL*/api_jsonrpc.php"
headers = {'Content-Type': 'application/json'}
#Деактивация хоста
payload = json.dumps({
    "jsonrpc": "2.0",
    "method": "host.update",
    "params": {
        "hostid": sys.argv[1],
        "status": "1"
        },
    "auth": "*ADMIN TOKEN*",#API_key
    "id": 1
})
requests.post(url, headers=headers, data=payload)

time.sleep(120)#задержка до активации хоста в секундах
#Активация хоста
payload = json.dumps({
    "jsonrpc": "2.0",
    "method": "host.update",
    "params": {
        "hostid": sys.argv[1],
        "status": "0"
        },
    "auth": "*ADMIN TOKEN*",#API_key
    "id": 1
})
requests.post(url, headers=headers, data=payload)
