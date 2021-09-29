import os
import re
import json

from datetime import datetime

import csv
import networkx as nx

StarFile = "../data/star2accounts.json"
WeiboFile = "../data/weibo.csv"
WeiboAtFile = "../data/weibo_ats.json"
KeywordFile = "../data/keywords.txt"
ReplaceFile = "../data/replace.txt"

Keyword2ID = {} # 保存关键词到下标的映射
Weibo2ID = {} # 保存微博序号到下标的映射
Star2ID = {} # 保存明星到下标的映射
Account2ID = {} # 保存账号到下标的映射
Account2Cate = {} # 保存账号到类型的映射

class GraphBuilder():
    def __init__(self, AccountReplace, gexf_file, json_file, category_file, time_upper_bound=None, time_lower_bound=None):
        self.save_gexf_file = gexf_file
        self.save_json_file = json_file
        self.category_file = category_file
        self.time_upper_bound = time_upper_bound
        self.time_lower_bound = time_lower_bound
        self.AccountReplace = AccountReplace
    
    def __replace_account(self, account):
        return self.AccountReplace.get(account, account)
        
    # StarFile
    def __add_star_node(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(StarFile, "r", encoding="utf-8")  as f:
            obj = json.load(f)
        for star in obj:
            if star not in Star2ID:
                Star2ID[star] = len(Star2ID)
            graph.add_node("Star%d"%Star2ID[star], type="Star", content=star)

    # StarFile
    # 这里只考虑初始的账户，有可能微博的at和转发会出现别的账户，那一部分将会留在添加边的过程中解决
    def __add_account_node(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(StarFile, "r", encoding="utf-8")  as f:
            obj = json.load(f)
        for star in obj:
            for account in obj[star]:
                account = self.__replace_account(account)
                if account not in Account2ID:
                    # print("In add_account:", account)
                    Account2ID[account] = len(Account2ID)
                if account not in Account2Cate:
                    Account2Cate[account] = 0
                graph.add_node("Account%d"%Account2ID[account], type="Account", category=Account2Cate[account], content=account)

    # KeywordFile
    def __add_keyword_node(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(KeywordFile, "r", encoding="utf-8") as f:
            line = f.readline()
            keywords = line.strip().split("、")
            for keyword in keywords:
                if keyword not in Keyword2ID:
                    Keyword2ID[keyword] = len(Keyword2ID)
                graph.add_node("Keyword%d"%Keyword2ID[keyword], type="Keyword", content=keyword) 

    # WeiboFile
    def __add_weibo_node(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(WeiboFile, "r", encoding="utf-8") as f:
            next(f) # skip the first line
            # f.readline()
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

    # StarFile Star->Account
    def __add_star_account_edge(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(StarFile, "r", encoding="utf-8")  as f:
            obj = json.load(f)
        for star in obj:
            for account in obj[star]:
                account = self.__replace_account(account)
                graph.add_edge("Star%d"%Star2ID[star], "Account%d"%Account2ID[account], type="HasAccount")
                graph.add_edge("Account%d"%Account2ID[account], "Star%d"%Star2ID[star], type="BelongToStar")
        pass

    # WeiboFile Weibo->Keyword
    def __add_weibo_keyword_edge(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(WeiboFile, "r", encoding="utf-8") as f:
            next(f) # skip the first line
            # f.readline()
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

    # WeiboFile Account->Weibo
    def __add_publish_edge(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(WeiboFile, "r", encoding="utf-8") as f:
            next(f) # skip the first line
            # f.readline()
            csv_reader = csv.reader(f)

            for line in csv_reader:
                index = line[0]
                author = line[2]
                author = self.__replace_account(author)
                if author not in graph.nodes:
                    if author not in Account2ID:
                        Account2ID[author] = len(Account2ID)
                    if author not in Account2Cate:
                        Account2Cate[author] = 0
                    graph.add_node("Account%d"%Account2ID[author], type="Account", category=Account2Cate[author], content=author)
                
                graph.add_edge("Account%d"%Account2ID[author], "Weibo%d"%Weibo2ID[index], type="PublishWeibo")
        pass

    # WeiboAtFile Weibo->Account
    def __add_at_edge(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(WeiboAtFile, "r", encoding="utf-8") as f:
            obj = json.load(f)
        for index in obj:
            for account in obj[index]:
                
                account = self.__replace_account(account)
                # 图中没有这个节点
                if account not in graph.nodes:
                    if account not in Account2Cate:
                        Account2Cate[account] = 0
                    if account not in Account2ID:
                        Account2ID[account] = len(Account2ID)
                    graph.add_node("Account%d"%Account2ID[account], type="Account", category=Account2Cate[account], content=account)

                graph.add_edge("Weibo%d"%Weibo2ID[index], "Account%d"%Account2ID[account], type="At", at_num=obj[index][account])
        pass

    # WeiboFile Account->Weibo
    def __add_forward_from_edge(self, graph:nx.classes.multidigraph.MultiDiGraph):
        with open(WeiboFile, "r", encoding="utf-8") as f:
            next(f) # skip the first line
            # f.readline()
            csv_reader = csv.reader(f)

            for line in csv_reader:
                index = line[0]
                forward_from = line[14]
                if not forward_from:
                    continue
                forward_from = self.__replace_account(forward_from)
                # 图中没有这个节点
                if forward_from not in graph.nodes:
                    if forward_from not in Account2ID:
                        Account2ID[forward_from] = len(Account2ID)
                    if forward_from not in Account2Cate:
                        Account2Cate[forward_from] = 0
                    graph.add_node("Account%d"%Account2ID[forward_from], type="Account", category=Account2Cate[forward_from], content=forward_from)
                
                graph.add_edge("Account%d"%Account2ID[forward_from], "Weibo%d"%Weibo2ID[index], type="ForwardedFrom")
        pass

    # style of the input time string: %Y/%m/%d %H:%M:%S
    # for example: 2020/09/16 16:34:59
    def build_graph(self):

        global Keyword2ID, Weibo2ID, Star2ID, Account2ID, Account2Cate
        global StarFile, WeiboFile, WeiboAtFile, KeywordFile
        
        '''
        从上次保存处恢复建图
        '''
        graph = nx.MultiDiGraph()
        
        if os.path.exists(self.save_json_file):
            with open(self.save_json_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                Keyword2ID = json.loads(lines[0])
                Weibo2ID = json.loads(lines[1])
                Star2ID = json.loads(lines[2])
                Account2ID = json.loads(lines[3])
        if os.path.exists(self.category_file):
            with open(self.category_file, "r", encoding="utf-8") as f:
                Account2Cate = json.load(f)
        
        '''
        筛选时间段
        '''
        if self.time_lower_bound and self.time_upper_bound:
            self.time_lower_bound = datetime.strptime(self.time_lower_bound, "%Y/%m/%d %H:%M:%S")
            self.time_upper_bound = datetime.strptime(self.time_upper_bound, "%Y/%m/%d %H:%M:%S")

            # new folder
            if not os.path.isdir("./tmp"):
                os.mkdir("./tmp")

            # filter weibo posts and write into new files
            newWeiboFile = "./tmp/weibo.csv"
            newWeiboAtFile = "./tmp/weibo_ats.json"
            filtered_weibo_indexes = []

            with open(WeiboFile, "r", encoding="utf-8") as inf, open(newWeiboFile, "w", encoding="utf-8", newline="") as outf:
                line = inf.readline()
                outf.write(line)
                csv_reader = csv.reader(inf)
                csv_writer = csv.writer(outf)
                for line in csv_reader:
                    index = line[0]
                    try:
                        t = datetime.strptime(line[3], "%Y/%m/%d %H:%M:%S")
                    except ValueError:
                        t = datetime.strptime(line[3], "%Y-%m-%d %H:%M:%S")
                    if self.time_lower_bound <= t and t <= self.time_upper_bound:
                        filtered_weibo_indexes.append(index)
                        csv_writer.writerow(line)
            # print(filtered_weibo_indexes)
            with open(WeiboAtFile, "r", encoding="utf-8") as f:
                obj = json.load(f)
            filtered_weibo_indexes = set(filtered_weibo_indexes)
            new_weibo_ats = {key: value for (key, value) in obj.items() if key in filtered_weibo_indexes}
            with open(newWeiboAtFile, "w", encoding="utf-8") as f:
                json.dump(new_weibo_ats, f, ensure_ascii=False)
            
            WeiboFile = newWeiboFile
            WeiboAtFile = newWeiboAtFile

        '''
        建图
        '''
        # add nodes
        self.__add_star_node(graph)
        self.__add_account_node(graph)
        self.__add_keyword_node(graph)
        self.__add_weibo_node(graph)

        # add edges
        self.__add_star_account_edge(graph)
        self.__add_weibo_keyword_edge(graph)
        self.__add_publish_edge(graph)
        self.__add_at_edge(graph)
        self.__add_forward_from_edge(graph)

        '''
        保存建图结果
        '''
        nx.write_gexf(graph, self.save_gexf_file)
        with open(self.save_json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(Keyword2ID, ensure_ascii=False)+"\n")
            f.write(json.dumps(Weibo2ID, ensure_ascii=False)+"\n")
            f.write(json.dumps(Star2ID, ensure_ascii=False)+"\n")
            f.write(json.dumps(Account2ID, ensure_ascii=False)+"\n")
        
        with open(self.category_file, "w", encoding="utf-8") as f:
            json.dump(Account2Cate, f, ensure_ascii=False)

def main(AccountReplace, gexf_file, json_file, category_file, time_upper_bound, time_lower_bound):
    print(time_lower_bound, "-", time_upper_bound)
    if os.path.exists(gexf_file):
        os.remove(gexf_file)
    if os.path.exists(json_file) and time_lower_bound == "2020/01/20 00:00:00" and time_upper_bound =="2020/09/18 00:00:00":
        os.remove(json_file)
    graph_builder = GraphBuilder(AccountReplace, gexf_file, json_file, category_file, time_upper_bound, time_lower_bound)
    graph_builder.build_graph()

if __name__ == "__main__":
    # 建图
    # 20200120 20200220 20200317 20200428 20200918
    # global WeiboAtFile, WeiboFile, KeywordFile, StarFile
    times = ["0120", "0220", "0317", "0428", "0918"]
    AccountReplace = {}
    with open(ReplaceFile, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.strip().split(" ")
            AccountReplace[splits[0]] = splits[1]

    for i in range(len(times)):
        for j in range(len(times)-1, i, -1):
            time_lower_bound = "2020/{}/{} 00:00:00".format(times[i][:2], times[i][2:])
            time_upper_bound = "2020/{}/{} 00:00:00".format(times[j][:2], times[j][2:])
            gexf_file = "../builds/graph_from_{}_to_{}.gexf".format(times[i], times[j])
            json_file = "../builds/tokens.json"
            category_file = "../builds/category.json"
            main(AccountReplace, gexf_file, json_file, category_file, time_upper_bound, time_lower_bound)

            WeiboFile = "../data/weibo.csv"
            WeiboAtFile = "../data/weibo_ats.json"
            # break