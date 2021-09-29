import os
import json
from queue import Queue

import networkx as nx
import matplotlib.pyplot as plt

class GraphBuilderForGephi(object):
    def __init__(self, raw_gexf_file, account2idx_file):
        # if os.path.exists(save_gexf_file):
        #     return
        with open(account2idx_file, "r", encoding="utf-8") as f:
            next(f)
            next(f)
            next(f)
            account2idx = json.loads(f.readline())
        self.idx2account = {value: key for key, value in account2idx.items()}
        self.special_graph = nx.DiGraph()

        raw_graph = nx.read_gexf(raw_gexf_file)
        self.graph = nx.DiGraph()

        for n, nbrs in raw_graph.adj.items():
            if "Account" not in n:
                continue
            for nbr, _ in nbrs.items():
                if "Weibo" not in nbr:
                    continue
                for nbr_nbr in raw_graph.neighbors(nbr):
                    if "Account" not in nbr_nbr:
                        continue
                    st = self.idx2account[int(n[7:])]
                    ed = self.idx2account[int(nbr_nbr[7:])]
                    if self.graph.has_edge(st, ed):
                        self.graph[st][ed]["weight"] += 1
                    else:
                        self.graph.add_node(st, category=raw_graph.nodes[n]["category"])
                        self.graph.add_node(ed, category=raw_graph.nodes[nbr_nbr]["category"])
                        # self.graph.add_node(ed, category=)
                        self.graph.add_edge(st, ed, weight=1)
        
    def save_graph(self, save_gexf_file):
        nx.write_gexf(self.graph, save_gexf_file)
    
    def save_special_graph(self, save_gexf_file):
        nx.write_gexf(self.special_graph, save_gexf_file)
    
    def filter_with_special_node(self, accounts, max_step=1):
        # outward
        que = Queue(maxsize=0)
        second_que = Queue(maxsize=0)
        for account in accounts:
            if account in self.graph.nodes:
                self.special_graph.add_node(account, category=self.graph.nodes[account]["category"])
                que.put(account)
            else:
                print("Error happend with given account: {}".format(account))

        round_cnt = 0
        while not que.empty() and round_cnt < max_step:
            while not que.empty():
                account = que.get()
                for nbr in self.graph.neighbors(account):
                    if self.special_graph.has_edge(account, nbr):
                        continue
                    if nbr not in self.special_graph.nodes:
                        self.special_graph.add_node(nbr, category=self.graph.nodes[nbr]["category"])
                    self.special_graph.add_edge(account, nbr, weight=self.graph[account][nbr]["weight"])
                    second_que.put(nbr)
            que = second_que
            round_cnt += 1
        
        # inward
        que = Queue(maxsize=0)
        second_que = Queue(maxsize=0)
        for account in accounts:
            if account in self.graph.nodes:
                # self.special_graph.add_node(account, category=self.graph.nodes[account]["category"])
                que.put(account)
            else:
                print("Error happend with given account: {}".format(account))

        round_cnt = 0
        while not que.empty() and round_cnt < max_step:
            while not que.empty():
                account = que.get()
                for parent in self.graph.nodes:
                    if not self.graph.has_edge(parent, account):
                        continue
                    if parent not in self.special_graph.nodes:
                        self.special_graph.add_node(parent, category=self.graph.nodes[parent]["category"])
                    self.special_graph.add_edge(parent, account, weight=self.graph[parent][account]["weight"])
                    second_que.put(parent)
            que = second_que
            round_cnt += 1
        

def main(start_month_day, end_month_day):
    raw_gexf_file = "../builds/graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    account2idx_file = "../builds/tokens.json"
    save_gexf_file = "../draw/graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    gbfg = GraphBuilderForGephi(raw_gexf_file, account2idx_file)
    gbfg.save_graph(save_gexf_file)

def main_with_special_nodes(start_month_day, end_month_day, accounts, max_step=1):
    raw_gexf_file = "../builds/graph_from_{}_to_{}.gexf".format(start_month_day, end_month_day)
    account2idx_file = "../builds/tokens.json"
    save_gexf_file = "../draw/graph_from_{}_to_{}_given_{}.gexf".format(start_month_day, end_month_day, "#".join(accounts))
    gbfg = GraphBuilderForGephi(raw_gexf_file, account2idx_file)
    gbfg.filter_with_special_node(accounts, max_step=max_step)
    gbfg.save_special_graph(save_gexf_file)

def enumerate_call_main():
    date_list = ["0120", "0220", "0317", "0428", "0918"]
    for i in range(len(date_list)):
        for j in range(i + 1, len(date_list)):
            main(date_list[i], date_list[j])
    
singles = [
    ["姚晨"],
    ["杨幂"],
    ["努力努力再努力x"],
    ["努力努力再努力x", "张艺兴工作室", "张艺兴吧_XingPark"],
    ["UNIQ-王一博"],
    ["UNIQ-王一博", "王一博粉丝后援会", "王一博吧_WYBBar"],
    ["西藏昌都人韩红"],
    ["西藏昌都人韩红", "韩红工作室", "韩红爱心慈善基金会"],
    ["高晓松"],
    ["相信未来义演"],
    ["朱一龙工作室"],
    ["明星粉丝联盟"],
    ["王俊凯微吧"],
    ["人民日报"],
    ["央视新闻"],
    ["中国电影报道"],
    ["共青团中央"],
    ["武汉发布"],
    ["世界卫生组织"],
    ["中华思源工程扶贫基金会"],
    ["韩红爱心慈善基金会"],
    ["肯德基"],
    ["大麦网"],
    ["宝洁中国"],
    ["抽风手戴老湿"],
    ["五七"],
    ["梁钰stacey"],
    ["希望世界和平的天使"],
    ["小梅迟子"]
]

if __name__ == "__main__":
    # main("0120", "0220")
    # enumerate_call_main()
    for single in singles:
        main_with_special_nodes("0120", "0918", single, max_step=1)
    