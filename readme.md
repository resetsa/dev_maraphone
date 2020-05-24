Финальное задание.
===================================

### Используемые модули:
* nornir
* networkx
* [GitHub Pages] (https://github.com/networktocode/ntc-templates)

### Тренировочное задание, в работе НЕ ИСПОЛЬЗОВАТЬ.
------------

#### Инструкция по запуску и применению:

В проекте 2 py файла:

* build_schema.py  
Генерация топологии, путем опроса сетевых устройства и вывода схемы в файл в той же директории  
Примечания:
  - Используется топология описанная в каталоге inventory/  
  - Пароль вынесен в сам скрипт (с целью последующего улучшения скрипта)  
  - Включен режим логирования уровня DEBUG  
  - При отрисовке топологии, если между устройствами больше 1 линка, то толщина линии увеличивается (второй линк не рисуется)  
  - В скрипте также производится проверка, на дублирование hostname устройств, с этой целью производится анализ связки chassis_id:hostname  
  - Предварительно сделать клон [GitHub Pages] (https://github.com/networktocode/ntc-templates) в домашнюю директорию.
Пример запуска:
```
sas@ans-01 ~/lldp_schema $ python3 build_schema.py
2020-05-05 23:36:37,348 - INFO - Start program for build network schema
2020-05-05 23:36:37,379 - DEBUG - Set default properties
2020-05-05 23:36:37,379 - DEBUG - Get lldp neighbors from device and fill property lldp
2020-05-05 23:36:37,379 - INFO - Running task 'netmiko_send_command' with args {'command_string': 'show lldp neighbors', 'use_textfsm': True} on 5 hosts
2020-05-05 23:36:37,381 - DEBUG - Host 'r1': running task 'netmiko_send_command'
2020-05-05 23:36:37,383 - DEBUG - Host 'sw5': running task 'netmiko_send_command'
2020-05-05 23:36:37,384 - DEBUG - Host 'sw4': running task 'netmiko_send_command'
2020-05-05 23:36:37,390 - DEBUG - Host 'sw6': running task 'netmiko_send_command'
2020-05-05 23:36:37,392 - DEBUG - Host 'sw7': running task 'netmiko_send_command'
2020-05-05 23:36:43,729 - DEBUG - Fill lldp table for r1
2020-05-05 23:36:43,729 - DEBUG - No neighbors on device r1
2020-05-05 23:36:43,730 - DEBUG - Fill lldp table for sw5
2020-05-05 23:36:43,730 - DEBUG - Fill lldp table for sw4
2020-05-05 23:36:43,731 - DEBUG - Fill lldp table for sw6
2020-05-05 23:36:43,731 - DEBUG - Fill lldp table for sw7
2020-05-05 23:36:43,732 - DEBUG - Get lldp neighbors detail from device and fill property lldp
2020-05-05 23:36:43,733 - INFO - Running task 'netmiko_send_command' with args {'command_string': 'show lldp neighbors detail', 'use_textfsm': True} on 5 hosts
2020-05-05 23:36:43,735 - DEBUG - Host 'r1': running task 'netmiko_send_command'
2020-05-05 23:36:43,736 - DEBUG - Host 'sw5': running task 'netmiko_send_command'
2020-05-05 23:36:43,736 - DEBUG - Host 'sw4': running task 'netmiko_send_command'
2020-05-05 23:36:43,737 - DEBUG - Host 'sw6': running task 'netmiko_send_command'
2020-05-05 23:36:43,740 - DEBUG - Host 'sw7': running task 'netmiko_send_command'
2020-05-05 23:36:44,640 - DEBUG - Fill lldp table for r1
2020-05-05 23:36:44,640 - DEBUG - No neighbors on device r1
2020-05-05 23:36:44,640 - DEBUG - Fill lldp table for sw5
2020-05-05 23:36:44,640 - DEBUG - Fill lldp table for sw4
2020-05-05 23:36:44,640 - DEBUG - Fill lldp table for sw6
2020-05-05 23:36:44,641 - DEBUG - Fill lldp table for sw7
2020-05-05 23:36:44,641 - DEBUG - Get interface from device on fill property interfaces
2020-05-05 23:36:44,641 - INFO - Running task 'netmiko_send_command' with args {'command_string': 'show interface', 'use_textfsm': True} on 5 hosts
2020-05-05 23:36:44,642 - DEBUG - Host 'r1': running task 'netmiko_send_command'
2020-05-05 23:36:44,642 - DEBUG - Host 'sw5': running task 'netmiko_send_command'
2020-05-05 23:36:44,643 - DEBUG - Host 'sw4': running task 'netmiko_send_command'
2020-05-05 23:36:44,645 - DEBUG - Host 'sw6': running task 'netmiko_send_command'
2020-05-05 23:36:44,646 - DEBUG - Host 'sw7': running task 'netmiko_send_command'
2020-05-05 23:36:45,652 - DEBUG - Fill interface table for r1
2020-05-05 23:36:45,653 - DEBUG - Fill interface table for sw5
2020-05-05 23:36:45,653 - DEBUG - Fill interface table for sw4
2020-05-05 23:36:45,653 - DEBUG - Fill interface table for sw6
2020-05-05 23:36:45,653 - DEBUG - Fill interface table for sw7
2020-05-05 23:36:45,653 - INFO - Running task 'napalm_get' with args {'getters': ['get_facts']} on 5 hosts
2020-05-05 23:36:45,654 - DEBUG - Host 'r1': running task 'napalm_get'
2020-05-05 23:36:45,655 - DEBUG - Host 'sw5': running task 'napalm_get'
2020-05-05 23:36:45,656 - DEBUG - Host 'sw4': running task 'napalm_get'
2020-05-05 23:36:45,658 - DEBUG - Host 'sw6': running task 'napalm_get'
2020-05-05 23:36:45,659 - DEBUG - Host 'sw7': running task 'napalm_get'
2020-05-05 23:36:53,576 - DEBUG - Fill facts table for r1
2020-05-05 23:36:53,576 - DEBUG - Fill facts table for sw5
2020-05-05 23:36:53,577 - DEBUG - Fill facts table for sw4
2020-05-05 23:36:53,577 - DEBUG - Fill facts table for sw6
2020-05-05 23:36:53,578 - DEBUG - Fill facts table for sw7
2020-05-05 23:36:53,579 - DEBUG - min mac aabb.cc00.1000
2020-05-05 23:36:53,579 - DEBUG - min mac aabb.cc00.5000
2020-05-05 23:36:53,580 - DEBUG - min mac aabb.cc00.4000
2020-05-05 23:36:53,580 - DEBUG - min mac aabb.cc00.6000
2020-05-05 23:36:53,581 - DEBUG - min mac aabb.cc00.7000
2020-05-05 23:36:53,582 - DEBUG - Add nodes aabb.cc00.1000
2020-05-05 23:36:53,583 - DEBUG - Add nodes aabb.cc00.5000
2020-05-05 23:36:53,583 - DEBUG - Add nodes aabb.cc00.7000
2020-05-05 23:36:53,584 - DEBUG - Add nodes aabb.cc00.6000
2020-05-05 23:36:53,584 - DEBUG - Add nodes aabb.cc00.4000
2020-05-05 23:36:53,584 - DEBUG - Add nodes aabb.cc00.4000
2020-05-05 23:36:53,585 - DEBUG - Add nodes aabb.cc00.6000
2020-05-05 23:36:53,585 - DEBUG - Add nodes aabb.cc00.2000
2020-05-05 23:36:53,586 - DEBUG - Add nodes aabb.cc00.7000
2020-05-05 23:36:53,586 - DEBUG - Add nodes aabb.cc00.3000
2020-05-05 23:36:53,587 - DEBUG - Check duplicate names in lldp neighbors
2020-05-05 23:36:53,731 - DEBUG - process links sw7 sw5
2020-05-05 23:36:53,732 - DEBUG - add link Et0/2
2020-05-05 23:36:53,745 - DEBUG - process links sw6 sw5
2020-05-05 23:36:53,745 - DEBUG - add link Et0/1
2020-05-05 23:36:53,756 - DEBUG - process links sw4 sw5
2020-05-05 23:36:53,757 - DEBUG - add link Et0/0
2020-05-05 23:36:53,770 - DEBUG - process links r3 sw7
2020-05-05 23:36:53,771 - DEBUG - add link Et0/3
2020-05-05 23:36:53,783 - DEBUG - process links sw6 sw7
2020-05-05 23:36:53,784 - DEBUG - add link Et0/2
2020-05-05 23:36:53,796 - DEBUG - process links sw5 sw7
2020-05-05 23:36:53,797 - DEBUG - add link Et0/1
2020-05-05 23:36:53,809 - DEBUG - process links r2 sw6
2020-05-05 23:36:53,810 - DEBUG - add link Et0/3
2020-05-05 23:36:53,822 - DEBUG - process links sw7 sw6
2020-05-05 23:36:53,823 - DEBUG - add link Et0/2
2020-05-05 23:36:53,835 - DEBUG - process links sw5 sw6
2020-05-05 23:36:53,836 - DEBUG - add link Et0/1
2020-05-05 23:36:53,848 - DEBUG - process links sw4 sw6
2020-05-05 23:36:53,849 - DEBUG - add link Et0/0
2020-05-05 23:36:53,863 - DEBUG - process links r1 sw4
2020-05-05 23:36:53,864 - DEBUG - add link Et0/0
2020-05-05 23:36:53,877 - DEBUG - process links sw6 sw4
2020-05-05 23:36:53,878 - DEBUG - add link Et0/2
2020-05-05 23:36:53,890 - DEBUG - process links sw5 sw4
2020-05-05 23:36:53,891 - DEBUG - add link Et0/1
2020-05-05 23:36:54,844 - INFO - End program for build network schema
```

* compare_dot.py  
Сравнение топологий и вывод результата  
Примечания: 
  - Изменения отрисовываются красным цветов
  - Есть проблема с экспортом/импортов dot файла описания графа.  
  После импорта связи класса MultiDiGraph описываются в формате (begin,end),а не (begin,end,count_link).  Поле count_link уходит в аттрибуты.  
  Есть подозрение, что я делаю что-то не так.

Пример запуска (по-умолчанию включен debug):
```
sas@ans-01 ~/lldp_schema $ python3 compare_dot.py -p topology_2020-05-05_162435.dot -n topology_2020-05-05_163140.dot -r result.png
2020-05-06 00:09:25,455 - INFO - Start program for compare network schema
2020-05-06 00:09:25,455 - DEBUG - Namespace(file_now='topology_2020-05-05_163140.dot', file_prev='topology_2020-05-05_162435.dot', file_result='result.png')
2020-05-06 00:09:25,455 - DEBUG - Try read dot files with network schema
2020-05-06 00:09:25,455 - INFO - Read file topology_2020-05-05_162435.dot
2020-05-06 00:09:25,733 - INFO - Read file topology_2020-05-05_163140.dot
2020-05-06 00:09:26,069 - INFO - Changes were exists
2020-05-06 00:09:26,521 - INFO - Save diff schema to result.png
2020-05-06 00:09:27,245 - INFO - End program for compare network schema
```
