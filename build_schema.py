import logging
import re

from time import gmtime, strftime

from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks.networking import napalm_get
from networkx.drawing.nx_pydot import write_dot

import networkx as nx
import matplotlib.pyplot as plt

#Пароль можно указать здесь или в файле config.yaml
PASSWORD = 'devnet'


def nornir_fill_lldp(task):
    """
    Функция для заполнения данных сведениями от lldp соседях
    В качестве параметра передается обьектов nornir.core.Nornir
    В результате работы заполняет свойство lldp
    """
    logger = logging.getLogger('nornir')
    logger.debug('Get lldp neighbors from device and fill property lldp')
    #Выполянем запрос данных от сетевых устройств
    out = task.run(task=netmiko_send_command,
                   command_string="show lldp neighbors", use_textfsm=True)
    #Проверям, что таск отработал штатн
    if out.failed:
        # Если хотя бы одно устройство не доступно, помечаем его ошибочным
        for h in out.failed_hosts.keys():
            logger.warning('Failed task on device %s', h)
            task.inventory.hosts[h]['error'] = True
    #Для всех остальных заполняем результат
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill lldp table for %s', h)
            # Если данные удалось распарсить,то заполяем свойство lldp
            if isinstance(r.result, list):
                task.inventory.hosts[h]['lldp'] = r.result
            else:
                logger.debug('No neighbors on device %s', h)
            task.inventory.hosts[h]['error'] = False


def nornir_fill_lldp_detail(task):
    """
    Функция для заполнения данных от выполнения show lldp neigborns detail
    В качестве параметра передается обьектов nornir.core.Nornir
    В результате работы заполняем свойства lldp_detail
    """
    logger = logging.getLogger('nornir')
    logger.debug(
        'Get lldp neighbors detail from device and fill property lldp')
    out = task.run(task=netmiko_send_command,
                   command_string="show lldp neighbors detail", use_textfsm=True)
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning('Failed task on device %s', h)
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill lldp table for %s', h)
            if isinstance(r.result, list):
                task.inventory.hosts[h]['lldp_detail'] = r.result
            else:
                logger.debug('No neighbors on device %s', h)
            task.inventory.hosts[h]['error'] = False


def nornir_fill_interface_exist(task):
    """
    Функция получения списка интерфейсов на устройствах
    В качестве параметра передается обьектов nornir.core.Nornir
    В результате работы заполняем свойства interfaces
    """
    logger = logging.getLogger('nornir')
    logger.debug('Get interface from device on fill property interfaces')
    out = task.run(task=netmiko_send_command,
                   command_string="show interface", use_textfsm=True)
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning('Failed task on device %s', h)
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill interface table for %s', h)
            task.inventory.hosts[h]['interfaces'] = r.result
            task.inventory.hosts[h]['error'] = False


def fill_chassis_id(task):
    """
    Функция получения chassisid управляемых устройств
    В качестве параметра передается обьектов nornir.core.Nornir
    В результате работы заполняем свойства chassis_id
    """
    logger = logging.getLogger('nornir')
    for h in task.inventory.hosts.keys():
        mac_list = list()
        # Строим список MAC адресов интерфейсов
        for i in task.inventory.hosts[h]['interfaces']:
            mac_list.append(i['address'])
        # Получаем самый младший адрес и заполняем свойство chassis_id
        logger.debug('min mac %s', get_low_mac(mac_list))
        task.inventory.hosts[h]['chassis_id'] = get_low_mac(mac_list)


def nornir_napalm_get_facts(task):
    """
    Функция получения общих сведений с управляемых устройств
    В качестве параметра передается обьектов nornir.core.Nornir
    В результате работы заполняем свойства facts
    """
    logger = logging.getLogger('nornir')
    out = task.run(napalm_get, getters=['get_facts'])
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning("Failed task on %s", h)
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill facts table for %s', h)
            task.inventory.hosts[h]['facts'] = r.result['get_facts']
            task.inventory.hosts[h]['error'] = False


def nornir_init_property(task):
    """
    Функция инициализации кастомных свойств используемых позже
    В качестве параметра передается обьектов nornir.core.Nornir
    """
    logger = logging.getLogger('nornir')
    logger.debug('Set default properties')
    for h in task.inventory.hosts.keys():
        task.inventory.hosts[h]['lldp'] = []
        task.inventory.hosts[h]['lldp_detail'] = []
        task.inventory.hosts[h]['interfaces'] = []
        task.inventory.hosts[h]['chassis_id'] = ''
        task.inventory.hosts[h]['error'] = True


def create_graph(task):
    """
    Функция для генерации графа на основе полученных данных с управляемых устройств
    В качестве параметра передается обьектов nornir.core.Nornir
    В результате работы выдает обьект типа MultiDiGraph
    """
    logger = logging.getLogger('nornir')
    # Инициализируем граф
    graph = nx.MultiDiGraph()
    # Блок проверки уникальности hostname в lldp neigborns
    # Заполняем словарь вида chassis_id:hostname
    map_ch_hostname = dict()
    for h in task.inventory.hosts.keys():
        logger.debug('Add nodes %s', task.inventory.hosts[h]['chassis_id'])
        map_ch_hostname[task.inventory.hosts[h]['chassis_id']] = task.inventory.hosts[h]['facts']['hostname']
        for n in task.inventory.hosts[h]['lldp_detail']:
            if n['chassis_id'] not in map_ch_hostname.keys():
                logger.debug('Add nodes %s', n['chassis_id'])
                map_ch_hostname[n['chassis_id']] = re.split(r"\.", n['neighbor'])[0]

    logger.debug('Check duplicate names in lldp neighbors')
    # Если дублирование нет, то заполяем структура графа
    if not check_duplicate_names(map_ch_hostname):
        for h in task.inventory.hosts.keys():
            # Добавляем управляенмые нами устройства
            graph.add_node(
                task.inventory.hosts[h]['facts']['hostname'], cap='')
            # проверяем соседей и если это устройство не управляется нами
            # добавляем на граф
            # дополнительно заполгяем свойство cap для неуправляемых нами
            # устройств
            for n in task.inventory.hosts[h]['lldp']:
                if n['neighbor'] not in graph.nodes():
                    graph.add_node(n['neighbor'], cap=n['capabilities'])
                # Иключаем линки с сабинтерфейсами
                if not (re.search(r"\.\d+", n['local_interface'])
                        or re.search(r"\.\d+", n['neighbor_interface'])):
                    # добавляем линк и заполняем аттирибут interfaces
                    graph.add_edge(h, n['neighbor'],
                                   interfaces=[n['local_interface'], n['neighbor_interface']])
    return graph


def output_graph(graph, filename_png, filename_dot):
    """
    Функция для вывод схемы в графический файл и файл описания .dot
    В качестве параметра передается обьект Graph
    В результате работы выводит в файлы filename_png/filename_dot
    Неоптимально и напоминает какие-то заклинания.
    Как пример ориентировался на
    https://github.com/dmfigol/nornir-apps/blob/master/scripts/build_network_diagram_lldp.py
    """

    logger = logging.getLogger('nornir')
    plt.subplots(figsize=(14, 9))
    pos = nx.spring_layout(graph)
    # Словари для генерации подписей
    el_b = dict()
    el_e = dict()
    # Проход по всем связям
    for b, e, c in graph.edges:
        logger.debug('process links %s %s'%(e, b))
        # Если линк встречает несколько раз, то сгенерировать
        # правильную подпись
        # и увеличить толщину линии
        if (b, e) in el_b.keys():
            logger.debug('key in dict,add int %s',
                         graph[b][e][c]['interfaces'][0])
            el_b[(b, e)] = el_b[(b, e)]+','+graph[b][e][c]['interfaces'][0]
            attr = dict()
            attr[(b, e, c)] = {'w': 4}
            nx.set_edge_attributes(graph, attr)
        else:
            logger.debug('add link %s', graph[b][e][c]['interfaces'][0])
            el_b[(b, e)] = graph[b][e][c]['interfaces'][0]
            attr = dict()
            attr[(b, e, c)] = {'w': 1}
            nx.set_edge_attributes(graph, attr)
            if (b, e) in el_e.keys():
                logger.debug('key int dict, add int %s',
                             graph[b][e][c]['interfaces'][1])
                el_e[(b, e)] = el_e[(b, e)]+','+graph[b][e][c]['interfaces'][1]
            else:
                el_e[(b, e)] = graph[b][e][c]['interfaces'][1]
        # Процедура рисования связей
        nx.draw_networkx_edges(graph, pos, edgelist=[(
            b, e, c)], edge_color='#00CCCC', width=graph[b][e][c]['w'])
    # Генерация подписей для хостов
    nodes_lab = dict()
    for h in graph.nodes():
        if not graph.nodes[h]['cap'] == '':
            nodes_lab[h] = h+'\n'+graph.nodes[h]['cap']
        else:
            nodes_lab[h] = h
    # Отрисовка остальной части графа
    nx.draw_networkx_nodes(graph, pos, node_size=1500, node_color='#00CCCC')
    nx.draw_networkx_labels(graph, pos, labels=nodes_lab, font_size=12)
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=el_b, label_pos=0.7, font_size=8)
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=el_e, label_pos=0.3, font_size=8)
    # Сохранение файлов
    plt.savefig(filename_png)
    write_dot(graph, filename_dot)


def get_low_mac(list_mac):
    """
    Функция для поиска самого младшего мак-а
    В качестве параметра передается обьект list мак
    В результате выдает младший.
    Пишу на Python 3 дня, скорее всего можно оптимальнее.
    """

    list_mac_hex = list()
    for mac in list_mac:
        list_mac_hex.append("0x"+''.join(re.split(r"\.", mac)))
        minpos = list_mac_hex.index(min(list_mac_hex))
    return list_mac[minpos]


def check_duplicate_names(d):
    """
    Функция для поиска дубликатов value в словаре.
    См. описание get_low_mac.
    """
    result = False
    logger = logging.getLogger('nornir')
    inv_d = dict()
    for k, v in d.items():
        if v not in inv_d.keys():
            inv_d[v] = k
        else:
            logger.warning("Duplicate hostname %s", v)
            result = True
    return result


def main():
    # Инициализация логгера
    logger = logging.getLogger('nornir')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info("Start program for build network schema")
    # Инициализация Nornir
    all_devices = InitNornir(config_file="config.yaml")
    # Установка пароля
    all_devices.inventory.defaults.password = PASSWORD

    nornir_init_property(all_devices)
    nornir_fill_lldp(all_devices)
    nornir_fill_lldp_detail(all_devices)
    nornir_fill_interface_exist(all_devices)
    nornir_napalm_get_facts(all_devices)
    fill_chassis_id(all_devices)

    network_graph = create_graph(all_devices)
    filename_png = 'topology_' + strftime("%Y-%m-%d_%H%M%S", gmtime())+'.png'
    filename_dot = 'topology_' + strftime("%Y-%m-%d_%H%M%S", gmtime())+'.dot'
    output_graph(network_graph, filename_png, filename_dot)

    logger.info("End program for build network schema")


if __name__ == "__main__":
    main()
