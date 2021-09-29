import os
import json

import networkx as nx
from networkx import algorithms
import numpy as np

class Clique(object):
    def __init__(self, raw_graph_gexf_file, save_adjacency_graph_file):
        self.graph = None
        self.__init(raw_graph_gexf_file, save_adjacency_graph_file)
    
    def __init(self, raw_graph_gexf_file, save_adjacency_graph_file):
        # if os.path.exists(save_adjacency_graph_file):
        #     self.graph = nx.read_gexf(save_adjacency_graph_file)
        #     return
        
        # 得到self.graph
        self.graph = nx.Graph()
        raw_graph = nx.read_gexf(raw_graph_gexf_file)
        for n, nbrs in raw_graph.adj.items():
            if "Account" not in n:
                continue
            for nbr, _ in nbrs.items():
                if "Weibo" not in nbr:
                    continue
                for nbr_nbr in raw_graph.neighbors(nbr):
                    if "Account" not in nbr_nbr:
                        continue
                    self.graph.add_edge(n, nbr_nbr)
        
        nx.write_gexf(self.graph, save_adjacency_graph_file)
    
    def calculate_clique(self, save_clique_file):
        f = open(save_clique_file, "w", encoding="utf-8")
        for clique in algorithms.clique.find_cliques(self.graph):
            f.write("{}\n".format(json.dumps(clique)))
            # print(clique)

def test():
    FG = nx.Graph()
    FG.add_nodes_from(["A1", "A2", "A3", "A4", "A5", "A6"])
    FG.add_edge("A1", "A2", type=1, weight=0)
    FG.add_edge("A1", "A3", type=2, weight=1)
    FG.add_edge("A2", "A3", type=4, weight=3)
    FG.add_edge("A3", "A5", type=3, weight=2)
    for clique in  algorithms.clique.find_cliques(FG):
        print(clique)
    # print(result, type(result))

def main(start_month_day, end_month_day):
    raw_graph_gexf_file = "../builds/graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    save_adjacency_graph_file = "../tmp/adjacency_undirected_graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    save_clique_file = "../result/cliques_from_{}_to_{}.txt".format(start_month_day, end_month_day)
    cent = Clique(raw_graph_gexf_file, save_adjacency_graph_file)
    cent.calculate_clique(save_clique_file)

if __name__ == "__main__":
    date_list = ["0120", "0220", "0317", "0428", "0918"]
    for i in range(len(date_list)):
        for j in range(i + 1, len(date_list)):
            main(date_list[i], date_list[j])
