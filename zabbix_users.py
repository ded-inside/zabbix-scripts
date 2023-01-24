# -*- coding: utf-8 -*-
import requests
import json
import pandas as pd

url = "*YOUR ZABBIX URL*/api_jsonrpc.php"
#получение списка пользователей
payload = json.dumps({
    "jsonrpc": "2.0",
    "method": "user.get",
    "params": {"output": ["username","roleid"]},
    "auth": "*ADMIN TOKEN*",
    "id": 2})
headers = {'Content-Type': 'application/json'}
answer = requests.post(url, headers=headers, data=payload).json()
user = answer["result"]
for element in user:
    del element['userid']
#получение списка ролей
payload = json.dumps({
    "jsonrpc": "2.0",
    "method": "role.get",
    "params": {"output": "extend","selectRules": "extend"},
    "auth": "*ADMIN TOKEN*",
    "id": 1})
headers = {'Content-Type': 'application/json'}
answer = requests.post(url, headers=headers, data=payload).json()
role = answer["result"]
for element in role:
  del element['readonly']
#построение одноуровнего словаря, удаление вложенностей и лишних данных
for elements in role:
  del elements['rules']['api']
  del elements['rules']['modules']
  del elements['type']
  for key in elements['rules']['actions']:
     key[key['name']]=key['status']
     del key['name']
     del key['status']
     elements[list(key.keys())[0]]=list(key.values())[0]
  for key in elements['rules']['ui']:
     key[key['name']]=key['status']
     del key['name']
     del key['status']
     elements[list(key.keys())[0]]=list(key.values())[0]
  del elements['rules']['actions']
  del elements['rules']['ui']
  for key,val in elements['rules'].items():
    elements[key]=val
  del elements['rules']

users = pd.DataFrame(user)#преобразование в таблицу
roles = pd.DataFrame(role)#преобразование в таблицу
users = users.fillna('0')#Замена пустых значений на 0
roles = roles.fillna('0')
sum_data=users.merge(roles,left_on='roleid',right_on='roleid')#Объединение 2х таблиц по roleid, и удаление этого столбца
del sum_data['roleid']
#Переименование столбцов
sum_data=sum_data.rename(columns={'username':'Логин','name':'Название роли','username':'Логин','edit_dashboards':'Изменение панелей','edit_maps':'Изменение карт','acknowledge_problems':'Подтверждение проблем',
'close_problems':'Закрытие проблем','change_severity':'Изменеие статуса проблем','add_problem_comments':'Добавление комментариев','execute_scripts':'Выполнение скриптов','manage_api_tokens':'Управление api токенами',
'edit_maintenance':'Изменение обслуживания','manage_scheduled_reports':'Управление регулярными отчетами','monitoring.dashboard':'Просмотр панелей','monitoring.problems':'Просмотр проблем','monitoring.hosts':'Просмотр хостов',
'monitoring.overview':'Просмотр обзора','monitoring.latest_data':'Просмотр последних данных','monitoring.maps':'Просмотр карт','monitoring.services':'Просмотр услуг','inventory.overview':'Просмотр инвентаризации',
'inventory.hosts':'Просмотр хостов инвентаризации','reports.availability_report':'Просмотр отчета о доступности','reports.top_triggers':'Просмотр отчета по триггерам','monitoring.discovery':'Просмотр обнаружения',
'reports.notifications':'Просмотр отчета оповещений','reports.scheduled_reports':'Просмотр запланированных отчетов','configuration.host_groups':'Настройка групп хостов',
'configuration.templates':'Настройка шаблонов','configuration.hosts':'Настройка хостов','configuration.maintenance':'Настройка обслуживания','configuration.actions':'Настройка действий','configuration.discovery':'Настройка обнаружения',
'configuration.services':'Настройка услуг','reports.system_info':'Просмотр отчета о системе','reports.audit':'Просмотр отчета аудита','reports.action_log':'Просмотр журнала действий',
'configuration.event_correlation':'Настройка корреляции событий','administration.general':'Администрирование','administration.proxies':'Настройка proxy','administration.authentication':'Настройка аутентификации',
'administration.user_groups':'Настройка групп пользователей','administration.user_roles':'Настройка ролей пользователей','administration.users':'Настройка пользователей','administration.media_types':'Настройка оповещений',
'administration.scripts':'Настройка скриптов','administration.queue':'Просмотр очереди','ui.default_access':'Доступ по умолчанию к новым элементам интерфейса','modules.default_access':'Доступ по умолчанию к новым модулям',
'api.access':'Доступ к api','api.mode':'Использование api','acknowledge_problems':'Подтверждение проблем','actions.default_access':'Доступ по умолчанию к новым действиям'})
#преобразование в csv и запись в файл
csv_data=sum_data.to_csv(index=False)
with open("Users.csv", "w") as file:
    file.write(csv_data)
