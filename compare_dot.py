from networkx.drawing.nx_pydot import write_dot,read_dot
import networkx as nx
import matplotlib.pyplot as plt
import logging
import argparse

def compare_schema(file_prev,file_now,file_result):
    logger = logging.getLogger('compare_schema')
    logger.debug('Try read dot files with network schema')
    logger.info('Read file '+file_prev)
    try:
        graph_prev=read_dot(file_prev)
    except:
        logger.error('Fail load schema')
        return
    logger.info('Read file '+file_now)
    try:
        graph_now=read_dot(file_now)
    except:
        logger.error('Fail to load schema')
        return

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.tight_layout()
    if nx.is_isomorphic(graph_prev,graph_now):
        logger.info('Schema is equal')
    else:
        logger.info('Changes were exists')
        graph_sum = nx.compose(graph_prev,graph_now)
        pos = nx.spring_layout(graph_sum)
        for n in graph_sum.nodes():
            if (n not in graph_prev.nodes() or n not in graph_now.nodes()):
                color='red'
            else:
                color='#00CCCC'
            nx.draw_networkx_nodes(graph_sum, pos, nodelist=[n],node_size=1500, node_color='#00CCCC')
        for b,e in graph_sum.edges():
            if (b,e) not in graph_prev.edges() or (b,e) not in graph_now.edges():
                color='red'
            else:
                color='#00CCCC'
            el_b=el_e=dict()
            nx.draw_networkx_edges(graph_sum, pos, edgelist=[([b,e])],edge_color=color)
            # Вот здесь прибито гвоздями
            # ПОчему при импорте есть проблема
            # Линки мультидиграф должны быть tuple вида
            # (источник.назначение,номер_линка)
            # после импорта, номер линка уезжает в аттрибут edge-а
            el_b[(b,e)]=graph_sum[b][e]['0']['interfaces']
            el_e[(b,e)]=graph_sum[b][e]['0']['interfaces']
            nx.draw_networkx_edge_labels(graph_sum, pos,edge_labels=el_b,label_pos=0.5,font_size=8,font_color=color)

        nodes_lab=dict()
        for h in graph_sum.nodes():
            if not graph_sum.nodes[h]['cap']=='':
                nodes_lab[h]=h+'\n'+graph_sum.nodes[h]['cap']
            else:
                nodes_lab[h]=h

        nx.draw_networkx_labels(graph_sum, pos, font_size=12)
        logger.info('Save diff schema to '+file_result)
        plt.savefig(file_result)

def main():
    parser = argparse.ArgumentParser(description='Compare schema script')
    parser.add_argument('-p', action="store", dest="file_prev",help="Source state file",required=True)
    parser.add_argument('-n', action="store", dest="file_now",help="Current state file",required=True)
    parser.add_argument('-r', action="store", dest="file_result",help="Result file",required=True)
    args = parser.parse_args()

    logger = logging.getLogger('compare_schema')
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info("Start program for compare network schema")
    logger.debug(args)
    compare_schema(args.file_prev,args.file_now,args.file_result)
    logger.info("End program for compare network schema")

if __name__ == "__main__":
    main()

