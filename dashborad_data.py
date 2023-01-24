# -*- coding: utf-8 -*-
import numpy
import requests
import json
import time
import datetime
import csv

#время по utc 
# lastday = datetime.datetime.utcnow().replace(day=1) - datetime.timedelta(days=1)
# oneday = datetime.datetime.utcnow().replace(day=1) - datetime.timedelta(days=lastday.day)
#время по gmt
lastday = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
oneday = datetime.date.today().replace(day=1) - datetime.timedelta(days=lastday.day)
time_begin = int(time.mktime(oneday.timetuple()))
time_end = int(time.mktime(lastday.timetuple()))

graph=[]
items=[]
history_max = []
history_avg = []
out = []
out_end = []
url = "http://*YOUR ZABBIX URL*/api_jsonrpc.php"
headers = {'Content-Type': 'application/json'}
#Получение списка виджетов
payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "dashboard.get",
        "params": {
        "selectPages": "extend",
        "dashboardids": ["63"]},
        "auth": "*YOUR TOKEN*",
        "id": 1})
answer = requests.post(url, headers=headers, data=payload).json()
answer1 = answer["result"][0]["pages"]
for pages in answer1:
    for widget in pages["widgets"]:
        dic={}
        dic[widget["name"]] = widget["fields"][0]["value"]
        graph.append(dic)
        del dic
#Получение списка элементов по виджетам
for item in graph:
    for val in item.values():
        payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "graphitem.get",
        "params": {
        "output": ["itemid","gitemid"],
        "graphids": val},
        "auth": "*YOUR TOKEN*",
        "id": 2})
        answer = requests.post(url, headers=headers, data=payload).json()
        answer = answer["result"]
        for slow in answer:
            dic={}
            dic[list(item.keys())[0]] = slow['itemid']
            items.append(dic)
            del dic

for id_data in items:
    for id in id_data.values():
        payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
        "output": ["name"],
        "itemids": id},
        "auth": "*YOUR TOKEN*",
        "id": 3})
        answer = requests.post(url, headers=headers, data=payload).json()
        answer2 = answer["result"][0]

        payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "trend.get",
        "params": {"output": ["value_avg","value_max"],
        "itemids": id,
        "time_from":time_begin,
        "time_till":time_end},
        "auth": "*YOUR TOKEN*",
        "id": 4})
        answer = requests.post(url, headers=headers, data=payload).json()
        answer = answer["result"]
        for key in answer:
            history_max.append(float(key['value_max']))
            history_avg.append(float(key['value_avg']))
        out.append(list(id_data.keys())[0])
        out.append(answer2["name"])
        try:
            aver=numpy.average(history_avg)
            maxim=max(history_max)
            out.append(int(aver/1000000))
            out.append(int(maxim/1000000))
        except ValueError:
            out.append("Nan")
        out_end.append(list(out))
        history_max = history_max.clear()
        history_avg = history_avg.clear()
        history_max = []
        history_avg = []
        out = out.clear()
        out = []
fields = ["Наименование НП","Наименование элемента данных","Средняя скорость Мб/с","Максимальная скорость Мб/с"]

with open(f'Траффик_c_{oneday}_по_{lastday}.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(fields)
    write.writerows(out_end)
