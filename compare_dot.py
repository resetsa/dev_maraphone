import logging
import argparse

from networkx.drawing.nx_pydot import read_dot
import networkx as nx
import matplotlib.pyplot as plt

'''
Early beta vsersion
Compare schema module
'''

def compare_schema(file_prev, file_now, file_result):
    '''
    Input - graph file in dot format
    Output - file in png format with diff
    '''
    logger = logging.getLogger('compare_schema')
    logger.debug('Try read dot files with network schema')
    logger.info('Read file {}'.format(file_prev))
    try:
        graph_prev = read_dot(file_prev)
    except IOError:
        logger.error('Fail load schema')
        return
    logger.info('Read file {}'.format(file_now))
    try:
        graph_now = read_dot(file_now)
    except IOError:
        logger.error('Fail to load schema')
        return

    fig = plt.subplots(figsize=(14, 9))
    if nx.is_isomorphic(graph_prev, graph_now):
        logger.info('Schema is equal')
    else:
        logger.info('Changes were exists')
        graph_sum = nx.compose(graph_prev, graph_now)
        pos = nx.spring_layout(graph_sum)
        for node in graph_sum.nodes():
            color = '#00CCCC'
            if node not in graph_prev.nodes() or node not in graph_now.nodes():
                color = 'red'
            nx.draw_networkx_nodes(graph_sum, pos, nodelist=[node],
                                   node_size=1500, node_color=color)
        for begin, end in graph_sum.edges():
            color = '#00CCCC'
            if (begin, end) not in graph_prev.edges() or (begin, end) not in graph_now.edges():
                color = 'red'
            el_b = el_e = dict()
            nx.draw_networkx_edges(graph_sum, pos, edgelist=[([begin, end])], edge_color=color)
            # Вот здесь прибито гвоздями
            # ПОчему при импорте есть проблема
            # Линки мультидиграф должны быть tuple вида
            # (источник.назначение,номер_линка)
            # после импорта, номер линка уезжает в аттрибут edge-а
            el_b[(begin, end)] = graph_sum[begin][end]['0']['interfaces']
            el_e[(begin, end)] = graph_sum[begin][end]['0']['interfaces']
            nx.draw_networkx_edge_labels(graph_sum, pos, edge_labels=el_b,
                                         label_pos=0.5, font_size=8, font_color=color)

        nodes_lab = dict()
        for host in graph_sum.nodes():
            if not graph_sum.nodes[host]['cap'] == '':
                nodes_lab[host] = host + '\n' + graph_sum.nodes[host]['cap']
            else:
                nodes_lab[host] = host

        nx.draw_networkx_labels(graph_sum, pos, font_size=12)
        logger.info('Save diff schema to {}'.format(file_result))
        plt.savefig(file_result)

def main():
    '''
    Main function
    '''
    parser = argparse.ArgumentParser(description='Compare schema script')
    parser.add_argument('-p', action="store", dest="file_prev",
                        help="Source state file", required=True)
    parser.add_argument('-n', action="store", dest="file_now",
                        help="Current state file", required=True)
    parser.add_argument('-r', action="store", dest="file_result",
                        help="Result file", required=True)
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
    compare_schema(args.file_prev, args.file_now, args.file_result)
    logger.info("End program for compare network schema")

if __name__ == "__main__":
    main()
