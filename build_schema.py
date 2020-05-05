from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.core.exceptions import NornirExecutionError
from nornir.plugins.tasks.networking import napalm_get
import sys
import logging
from time import gmtime, strftime

import networkx as nx
import matplotlib.pyplot as plt
import re


password = 'devnet'

def nornir_fill_lldp(task):
    logger = logging.getLogger('nornir')
    logger.debug('Get lldp neighbors from device and fill property lldp')
    out = task.run(task=netmiko_send_command,
                   command_string="show lldp neighbors", use_textfsm=True)
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning('Failed task on device '+h)
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill lldp table for ' + h)
            if isinstance(r.result,list):
                task.inventory.hosts[h]['lldp'] = r.result
            else:
                logger.debug('No neighbors on device '+h)
            task.inventory.hosts[h]['error'] = False

def nornir_fill_lldp_detail(task):
    logger = logging.getLogger('nornir')
    logger.debug('Get lldp neighbors detail from device and fill property lldp')
    out = task.run(task=netmiko_send_command,
                   command_string="show lldp neighbors detail", use_textfsm=True)
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning('Failed task on device '+h)
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill lldp table for ' + h)
            if isinstance(r.result,list):
                task.inventory.hosts[h]['lldp_detail'] = r.result
            else:
                logger.debug('No neighbors on device '+h)
            task.inventory.hosts[h]['error'] = False

def nornir_fill_interface_exist(task):
    logger = logging.getLogger('nornir')
    logger.debug('Get interface from device on fill property interfaces')
    out = task.run(task=netmiko_send_command,
                   command_string="show interface", use_textfsm=True)
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning('Failed task on device '+h)
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill interface table for ' + h)
            task.inventory.hosts[h]['interfaces'] = r.result
            task.inventory.hosts[h]['error'] = False

def fill_chassis_id(task):
    logger = logging.getLogger('nornir')
    for h in task.inventory.hosts.keys():
        mac_list=list()
        for i in task.inventory.hosts[h]['interfaces']:
            mac_list.append(i['address'])
        logger.debug('min mac ' + get_low_mac(mac_list))
        task.inventory.hosts[h]['chassis_id']=get_low_mac(mac_list)


def nornir_napalm_get_facts(task):
    logger = logging.getLogger('nornir')
    out = task.run(napalm_get, getters=['get_facts'])
    if out.failed:
        for h in out.failed_hosts.keys():
            logger.warning("Failed task on " + h + "")
            task.inventory.hosts[h]['error'] = True
    for h, r in out.items():
        if not r.failed:
            logger.debug('Fill facts table for ' + h)
            task.inventory.hosts[h]['facts'] = r.result['get_facts']
            task.inventory.hosts[h]['error'] = False


def nornir_init_property(task):
    logger = logging.getLogger('nornir')
    logger.debug('Set default properties')
    for h in task.inventory.hosts.keys():
        task.inventory.hosts[h]['lldp'] = []
        task.inventory.hosts[h]['lldp_detail'] = []
        task.inventory.hosts[h]['interfaces'] = []
        task.inventory.hosts[h]['chassis_id']=''
        task.inventory.hosts[h]['error'] = True

def create_graph(task):
    logger = logging.getLogger('nornir')
    graph = nx.MultiDiGraph()
    map_ch_hostname=dict()
    for h in task.inventory.hosts.keys():
        logger.debug('Add nodes '+task.inventory.hosts[h]['chassis_id'])
        map_ch_hostname[task.inventory.hosts[h]['chassis_id']]=task.inventory.hosts[h]['facts']['hostname']
        for n in task.inventory.hosts[h]['lldp_detail']:
            if n['chassis_id'] not in map_ch_hostname.keys():
                logger.debug('Add nodes '+n['chassis_id'])
                map_ch_hostname[n['chassis_id']]=re.split("\.",n['neighbor'])[0]
    logger.debug('Check duplicate names in lldp neighbors')
    if not check_duplicate_names(map_ch_hostname):
        for h in task.inventory.hosts.keys():
            graph.add_node(task.inventory.hosts[h]['facts']['hostname'],cap='RB')
            for n in task.inventory.hosts[h]['lldp']:
                if n['neighbor'] not in graph.nodes():
                    graph.add_node(n['neighbor'],cap=n['capabilities'])
                if not (re.search("\.\d+", n['local_interface']) or re.search("\.\d+", n['neighbor_interface'])):
                    graph.add_edge(h,n['neighbor'], interfaces=[n['local_interface'],n['neighbor_interface']])
    return graph

def output_graph(graph,filename):
    logger = logging.getLogger('nornir')
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.tight_layout()
    pos = nx.spring_layout(graph)
    el_b=dict()
    el_e=dict()
    for b,e,c in graph.edges:
        logger.debug('process links '+e+' '+b)
        if (b,e) in el_b.keys():
            logger.debug('key in dict,add int '+graph[b][e][c]['interfaces'][0])
            el_b[(b,e)]=el_b[(b,e)]+','+graph[b][e][c]['interfaces'][0]
            attr=dict()
            attr[(b,e,c)]={'w':4}
            nx.set_edge_attributes(graph, attr)
        else:
            logger.debug('add link '+graph[b][e][c]['interfaces'][0])
            el_b[(b,e)]=graph[b][e][c]['interfaces'][0]
            attr=dict()
            attr[(b,e,c)]={'w':1}
            nx.set_edge_attributes(graph, attr)
            if (b,e) in el_e.keys():
                logger.debug('key int dict, add int '+graph[b][e][c]['interfaces'][1])
                el_e[(b,e)]=el_e[(b,e)]+','+graph[b][e][c]['interfaces'][1]
            else:
                 el_e[(b,e)]=graph[b][e][c]['interfaces'][1]
        nx.draw_networkx_edges(graph, pos, edgelist=[(b,e,c)],edge_color='#00CCCC',width=graph[b][e][c]['w'])

    nodes_lab=dict()
    for h in graph.nodes():
        nodes_lab[h]=h+'\n'+graph.nodes[h]['cap']

    nx.draw_networkx_nodes(graph, pos, node_size=1500, node_color='#00CCCC')
    nx.draw_networkx_labels(graph, pos, labels=nodes_lab,font_size=12)
    nx.draw_networkx_edge_labels(graph, pos,edge_labels=el_b, label_pos=0.7,font_size=8)
    nx.draw_networkx_edge_labels(graph, pos,edge_labels=el_e, label_pos=0.3,font_size=8)
    plt.savefig(filename)

def get_low_mac(list_mac):
    list_mac_hex=list()
    for mac in list_mac:
        list_mac_hex.append("0x"+''.join(re.split("\.",mac)))
        minpos=list_mac_hex.index(min(list_mac_hex))
    return list_mac[minpos]

def check_duplicate_names(d:dict):
    result=False
    logger = logging.getLogger('nornir')
    inv_d=dict()
    for k,v in d.items():
        if v not in inv_d.keys():
            inv_d[v]=k
        else:
            logger.warning("Duplicate hostname "+v)
            result=True
    return result



def main():

    logger = logging.getLogger('nornir')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info("Start program for build network schema")

    all = InitNornir(config_file="/home/sas/nornir/config.yaml")
    all.inventory.defaults.password = password

    nornir_init_property(all)
    nornir_fill_lldp(all)
    nornir_fill_lldp_detail(all)
    nornir_fill_interface_exist(all)
    nornir_napalm_get_facts(all)
    fill_chassis_id(all)

    network_graph=create_graph(all)
    output_graph(network_graph,'topology.png')


    logger.info("End program for build network schema")


if __name__ == "__main__":
    main()
