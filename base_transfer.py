# -*- coding: utf-8 -*-
#Скрипт переносит всю информацию в указанных таблицах из одной базы заббикса в другую. Таблицы прописаны в переменной tables, в порядке зависимости таблиц в базе
import psycopg2
resbase = psycopg2.connect(dbname='*YOUR ZABBIX 6 DATABASE*', user='*YOUR USERNAME*', password='*YOUR PASSWORD*', host='*YOUR ZABBIX 6 DATABASE IP ADRESS*')#коннект к базе, куда кладутся данные
mainbase = psycopg2.connect(dbname='*YOUR ZABBIX 5 DATABASE*', user='*YOUR USERNAME*', password='*YOUR PASSWORD*', host='*YOUR ZABBIX 5 DATABASE IP ADRESS*')#коннект к базе, откуда берутся данные
curreserv = resbase.cursor()
curmain = mainbase.cursor()
tables = ["role","role_rule","usrgrp","users","users_groups","token","timeperiods","hstgrp","maintenances","hosts","hosts_groups","host_tag","hostmacro","hosts_templates","task","task_acknowledge",
"scripts","globalmacro","regexps","expressions","profiles","module","media_type","media_type_message","media_type_param","images","media","icon_map","icon_mapping","ids","interface",
"interface_snmp","valuemap","valuemap_mapping","items","item_tag","item_rtdata","item_preproc","item_parameter","item_discovery","item_condition","lld_override","lld_override_condition",
"lld_override_operation","lld_override_opdiscover","lld_override_opstatus","maintenances_groups","maintenances_hosts","maintenances_windows","actions","conditions",
"config","config_autoreg_tls","escalations","operations","opcommand","opcommand_hst","opgroup","opmessage","opmessage_grp","opmessage_usr","optemplate","triggers","trigger_tag","trigger_discovery","trigger_depends",
"dashboard","dashboard_page","dashboard_user","dashboard_usrgrp","graph_theme","graphs","graphs_items","graph_discovery","sysmaps","sysmap_usrgrp","sysmap_shape","sysmaps_elements",
"sysmaps_element_tag","sysmap_element_trigger","sysmap_element_url","sysmaps_links","sysmaps_link_triggers","widget","widget_field","functions","host_discovery"]
#удаление мещающих связей
curreserv.execute("ALTER TABLE public.items DROP CONSTRAINT c_items_5;")
curreserv.execute("ALTER TABLE public.items DROP CONSTRAINT c_items_2;")
curreserv.execute("ALTER TABLE public.triggers DROP CONSTRAINT c_triggers_1;")
curreserv.execute("ALTER TABLE public.graphs DROP CONSTRAINT c_graphs_1;")
# Очистка новой базы
for items in tables[::-1]:
    curreserv.execute(f"DELETE FROM {items};")
    print(f"Таблица {items} удалена")
ka = 0 #общая статистика
for items in tables:
    k = 0
    #получение списка колонок в каждой таблице обоих баз
    curmain.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{items}' and table_schema ='public';")
    b1 = curmain.fetchall()
    curreserv.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{items}' and table_schema ='public';")
    b2 = curreserv.fetchall()
    if set(b1) != set(b2):#сравнение списков
        b3 = list(set(b1) & set(b2))
        name_col = ''
        for i in b3:
            name_col = name_col + i[0]+","
        name_col = name_col[:-1]
        #выборка данных из старой базы и запись в новую
        curmain.execute(f"SELECT {name_col} FROM {items};")
        for row in curmain:
            s = len(row)
            val = "%s,"*s
            val = val[:-1]
            curreserv.execute(f"INSERT INTO {items} ({name_col}) VALUES({val})",row)
            k = k + 1
            ka = ka + 1
        print(k,f" записей добавлено в {items}")

    else:
        name_col =''
        for i in b1:
            name_col = name_col + i[0]+","
        name_col = name_col[:-1]
        #выборка данных из старой базы и запись в новую
        curmain.execute(f"SELECT * FROM {items};")
        for row in curmain:
            s = len(row)
            val = "%s,"*s
            val = val[:-1]
            curreserv.execute(f"INSERT INTO {items} ({name_col}) VALUES({val})",row)
            k = k + 1
            ka = ka + 1
        print(k,f" записей добавлено в {items}")
#восстановление удаленных связей
curreserv.execute("ALTER TABLE public.items ADD CONSTRAINT c_items_2 FOREIGN KEY (templateid) REFERENCES items(itemid);")
curreserv.execute("ALTER TABLE public.items ADD CONSTRAINT c_items_5 FOREIGN KEY (master_itemid) REFERENCES items(itemid)")
curreserv.execute("ALTER TABLE public.triggers ADD CONSTRAINT c_triggers_1 FOREIGN KEY (templateid) REFERENCES triggers(triggerid)")
curreserv.execute("ALTER TABLE public.graphs ADD CONSTRAINT c_graphs_1 FOREIGN KEY (templateid) REFERENCES graphs(graphid) ON DELETE CASCADE")

resbase.commit()#Сохранение изменений
mainbase.close()
resbase.close()
print(f"Успешно! Из {len(tables)} добавлено {ka} записей")
