import os

import networkx as nx

class Density(object):
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
    
    def calculate_graph_density(self, save_density_file):
        nodes = []
        for item in self.graph.edges:
            nodes.append(item[0])
            nodes.append(item[1])
        nodes = list(set(nodes))
        graph_density = len(self.graph.edges)/(len(nodes)*(len(nodes)-1))
        with open(save_density_file, "w", encoding="utf-8") as outf:
            outf.write("{}\n".format(graph_density))
    
def main(start_month_day, end_month_day):
    raw_graph_gexf_file = "../builds/graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    save_adjacency_graph_file = "../tmp/adjacency_graph_from_{}_{}.gexf".format(start_month_day, end_month_day)
    save_density_file = "../result/density_from_{}_to_{}.txt".format(start_month_day, end_month_day)
    dense = Density(raw_graph_gexf_file, save_adjacency_graph_file)
    dense.calculate_graph_density(save_density_file)

if __name__ == "__main__":
    date_list = ["0120", "0220", "0317", "0428", "0918"]
    for i in range(len(date_list)):
        for j in range(i + 1, len(date_list)):
            main(date_list[i], date_list[j])