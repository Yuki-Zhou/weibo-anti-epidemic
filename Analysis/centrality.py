import os
import json

import networkx as nx
from networkx import algorithms

class Centrality(object):
    def __init__(self, raw_graph_gexf_file, save_adjacency_graph_file):
        self.graph = None
        self.__init(raw_graph_gexf_file, save_adjacency_graph_file)
    
    def __init(self, raw_graph_gexf_file, save_adjacency_graph_file):
        # if os.path.exists(save_adjacency_graph_file):
        #     self.graph = nx.read_gexf(save_adjacency_graph_file)
        #     return
        
        # 得到self.graph
        self.graph = nx.DiGraph()
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
                    if self.graph.has_edge(n, nbr_nbr):
                        self.graph[n][nbr_nbr]["weight"] += 1
                    else:
                        self.graph.add_edge(n, nbr_nbr, weight=1)
        
        nx.write_gexf(self.graph, save_adjacency_graph_file)
    
    def calculate_betweenness_centrality(self):
        '''
        return:
            betweenness_centrality: dict{node: betweenness_centrality_score}
        '''
        return algorithms.betweenness_centrality(self.graph, weight="weight")
    
    def calculate_degree_centrality(self):
        '''
        returns:
            absolute node outdegree, absolute node indegree;
            realtive node outdegree, realtive node indegree;
            graph outdegree, graph indegree.
        '''
        in_degrees = algorithms.degree_alg.in_degree_centrality(self.graph)
        max_in_degree = max(list(in_degrees.values()))
        out_degrees = algorithms.degree_alg.out_degree_centrality(self.graph)
        max_out_degree = max(list(out_degrees.values()))
        relative_in_degrees = {key: value / max_in_degree for key, value in in_degrees.items()}
        relative_out_degrees = {key: value / max_out_degree for key, value in out_degrees.items()}
        graph_out_degree = sum([max_out_degree - value for value in list(out_degrees.values())])
        graph_in_degree = sum([max_in_degree - value for value in list(in_degrees.values())])
        return out_degrees, in_degrees, relative_out_degrees, relative_in_degrees, graph_out_degree, graph_in_degree
    
    def calculate_inward_closeness_centrality(self):
        return algorithms.closeness_centrality(self.graph)

    def calculate_outward_closeness_centrality(self):
        self.graph = self.graph.reverse()
        return algorithms.closeness_centrality(self.graph)

    def calculate_centrality(self, save_dir):
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        # 点度中心度
        out_degrees, in_degrees, relative_out_degrees, relative_in_degrees, graph_out_degree, graph_in_degree = self.calculate_degree_centrality()
        with open(os.path.join(save_dir, "outward_degree_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(out_degrees, ensure_ascii=False)))
        with open(os.path.join(save_dir, "inward_degree_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(in_degrees, ensure_ascii=False)))
        with open(os.path.join(save_dir, "relative_outward_degree_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(relative_out_degrees, ensure_ascii=False)))
        with open(os.path.join(save_dir, "relative_inward_degree_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(relative_in_degrees, ensure_ascii=False)))
        with open(os.path.join(save_dir, "graph_outward_degree_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(graph_out_degree))
        with open(os.path.join(save_dir, "graph_inward_degree_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(graph_in_degree))
        
        # 中间中心度
        betweenness_centrality = self.calculate_betweenness_centrality()
        with open(os.path.join(save_dir, "betweenness_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(betweenness_centrality, ensure_ascii=False)))

        # 接近中心度-入
        closeness_centrality = self.calculate_inward_closeness_centrality()
        with open(os.path.join(save_dir, "inward_closeness_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(closeness_centrality, ensure_ascii=False)))
        # 接近中心度-出
        closeness_centrality = self.calculate_outward_closeness_centrality()
        with open(os.path.join(save_dir, "outward_closeness_centrality.txt"), "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(json.dumps(closeness_centrality, ensure_ascii=False)))
        pass

def test():
    FG = nx.DiGraph()
    FG.add_nodes_from(["A1", "A2", "A3", "A4", "A5", "A6"])
    FG.add_edge("A1", "A2", type=1, weight=0)
    FG.add_edge("A1", "A3", type=2, weight=1)
    FG.add_edge("A3", "A5", type=3, weight=2)
    if "A1" in FG.nodes:
        print("zhe")
    result = algorithms.betweenness_centrality(FG, weight="weight")
    print(result, type(result))

def main(start_month_day, end_month_day):
    raw_graph_gexf_file = "../builds/graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    save_adjacency_graph_file = "../tmp/adjacency_graph_from_{}_{}.gexf".format(start_month_day, end_month_day)
    save_dir = "../result/centrality_from_{}_to_{}/".format(start_month_day, end_month_day)
    cent = Centrality(raw_graph_gexf_file, save_adjacency_graph_file)
    cent.calculate_centrality(save_dir)

if __name__ == "__main__":
    # test()
    date_list = ["0120", "0220", "0317", "0428", "0918"]
    for i in range(len(date_list)):
        for j in range(i + 1, len(date_list)):
            main(date_list[i], date_list[j])
