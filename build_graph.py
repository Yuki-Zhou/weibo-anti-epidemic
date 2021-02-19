import time
import sys
import os
import re
import json

import csv
import networkx as nx

StarFile = "./data/star2accounts.json"
WeiboFile = "./data/weibo.csv"
WeiboAtFile = "./data/weibo_ats.json"
KeywordFile = "./data/keywords.txt"

Keyword2ID = {} # 保存关键词到下标的映射
Weibo2ID = {} # 保存微博序号到下标的映射
Star2ID = {} # 保存明星到下标的映射
Account2ID = {} # 保存账号到下标的映射

# StarFile
def add_star_node(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(StarFile, "r", encoding="utf-8")  as f:
        obj = json.load(f)
    for star in obj:
        if star not in Star2ID:
            Star2ID[star] = len(Star2ID)
        graph.add_node("Star%d"%Star2ID[star], type="Star", content=star)

# StarFile
# 这里只考虑初始的账户，有可能微博的at和转发会出现别的账户，那一部分将会留在添加边的过程中解决
def add_account_node(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(StarFile, "r", encoding="utf-8")  as f:
        obj = json.load(f)
    for star in obj:
        for account in obj[star]:
            if account not in Account2ID:
                Account2ID[account] = len(Account2ID)
            graph.add_node("Account%d"%Account2ID[account], type="Account", content=account)

# KeywordFile
def add_keyword_node(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(KeywordFile, "r", encoding="utf-8") as f:
        line = f.readline()
        keywords = line.strip().split("、")
        for keyword in keywords:
            if keyword not in Keyword2ID:
                Keyword2ID[keyword] = len(Keyword2ID)
            graph.add_node("Keyword%d"%Keyword2ID[keyword], type="Keyword", content=keyword) 

# WeiboFile
def add_weibo_node(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(WeiboFile, "r", encoding="utf-8") as f:
        next(f) # skip the first line
        csv_reader = csv.reader(f)
        for line in csv_reader:
            index = line[0]
            if index not in Weibo2ID:
                Weibo2ID[index] = len(Weibo2ID)
            
            time = line[3]
            sentiment = line[7]
            forwards = line[10]
            comments = line[11]
            goods = line[12]
            kind = line[13]
            plays = line[15]

            if re.findall(r'\d+', plays):
                plays = int(re.findall(r'\d+', plays)[0])
            else:
                plays = 0

            graph.add_node("Weibo%d"%Weibo2ID[index], type="Weibo", time=time, 
                           sentiment=sentiment, forwards=forwards, comments=comments, 
                           goods = goods, kind=kind, plays=plays)
    pass

# StarFile
def add_star_account_edge(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(StarFile, "r", encoding="utf-8")  as f:
        obj = json.load(f)
    for star in obj:
        for account in obj[star]:
            graph.add_edge("Star%d"%Star2ID[star], "Account%d"%Account2ID[account], type="HasAccount")
            graph.add_edge("Account%d"%Account2ID[account], "Star%d"%Star2ID[star], type="BelongToStar")
    pass

# WeiboFile
def add_weibo_keyword_edge(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(WeiboFile, "r", encoding="utf-8") as f:
        next(f) # skip the first line
        csv_reader = csv.reader(f)

        for line in csv_reader:
            keywords = line[1].split(",")
            index = line[0]
            for keyword in keywords:
                if keyword not in Keyword2ID:
                    Keyword2ID[keyword] = len(Keyword2ID)
                    graph.add_node("Keyword%d"%Keyword2ID[keyword], type="Keyword", content=keyword)
                graph.add_edge("Weibo%d"%Weibo2ID[index], "Keyword%d"%Keyword2ID[keyword], type="HasKeyword")
    pass

# WeiboFile
def add_publish_edge(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(WeiboFile, "r", encoding="utf-8") as f:
        next(f) # skip the first line
        csv_reader = csv.reader(f)

        for line in csv_reader:
            index = line[0]
            author = line[2]

            graph.add_edge("Account%d"%Account2ID[author], "Weibo%d"%Weibo2ID[index], type="PublishWeibo")
    pass

# WeiboAtFile
def add_at_edge(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(WeiboAtFile, "r", encoding="utf-8") as f:
        obj = json.load(f)
    for index in obj:
        for account in obj[index]:
            if account not in Account2ID:
                Account2ID[account] = len(Account2ID)
                graph.add_node("Account%d"%Account2ID[account], type="Account", content=account)
            graph.add_edge("Weibo%d"%Weibo2ID[index], "Account%d"%Account2ID[account], type="At", at_num=obj[index][account])
    pass

# WeiboFile
def add_forward_from_edge(graph:nx.classes.multidigraph.MultiDiGraph):
    with open(WeiboFile, "r", encoding="utf-8") as f:
        next(f) # skip the first line
        csv_reader = csv.reader(f)

        for line in csv_reader:
            index = line[0]
            forward_from = line[14]
            if not forward_from:
                continue
            
            if forward_from not in Account2ID:
                Account2ID[forward_from] = len(Account2ID)
                graph.add_node("Account%d"%Account2ID[forward_from], type="Account", content=forward_from)
            graph.add_edge("Weibo%d"%Weibo2ID[index], "Account%d"%Account2ID[forward_from], type="ForwardedFrom")
    pass

def build_graph(gexf_file, json_file, time_upper_bound=None, time_lower_bound=None):

    global Keyword2ID, Weibo2ID, Star2ID, Account2ID
    global StarFile, WeiboFile, WeiboAtFile, KeywordFile
    
    '''
    从上次保存处恢复建图
    '''
    if os.path.exists(gexf_file):
        graph = nx.read_gexf(gexf_file)
    else:
        graph = nx.MultiDiGraph()
    
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            Keyword2ID = json.loads(lines[0])
            Weibo2ID = json.loads(lines[1])
            Star2ID = json.loads(lines[2])
            Account2ID = json.loads(lines[3])
    
    '''
    筛选时间段
    '''
    if time_lower_bound and time_upper_bound:
        pass

    '''
    建图
    '''
    # add nodes
    add_star_node(graph)
    add_account_node(graph)
    add_weibo_node(graph)
    add_keyword_node(graph)

    # add edges
    add_star_account_edge(graph)
    add_weibo_keyword_edge(graph)
    add_publish_edge(graph)
    add_at_edge(graph)
    add_forward_from_edge(graph)

    '''
    保存建图结果
    '''
    nx.write_gexf(graph, gexf_file)
    with open(json_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(Keyword2ID, ensure_ascii=False)+"\n")
        f.write(json.dumps(Weibo2ID, ensure_ascii=False)+"\n")
        f.write(json.dumps(Star2ID, ensure_ascii=False)+"\n")
        f.write(json.dumps(Account2ID, ensure_ascii=False)+"\n")

if __name__ == "__main__":
    gexf_file = "./builds/thegraph.gexf"
    json_file = "./builds/tokens.json"
    os.remove(gexf_file)
    os.remove(json_file)
    build_graph(gexf_file, json_file)