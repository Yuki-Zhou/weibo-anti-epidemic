import json
import re
import os
import csv
from datetime import datetime

import jieba
import jieba.posseg as jp
from gensim import corpora, models
# import pyLDAvis
import pyLDAvis.gensim_models

class WeiboPreprocess(object):
    def __init__(self, raw_weibo_file, save_weibo_file):
        self.raw_weibo_file = raw_weibo_file
        self.save_weibo_file = save_weibo_file

    def __clear_text(self, text):
        # 去除超链接
        text = re.sub(r"http.*?\s", "", text)
        # 去除中括号中的表情包
        text = re.sub(r"\[.+?\]", "", text)
        # 将连续的@分开
        text = re.sub(r"@", " @", text)
        # 将theme替换为空格
        text = re.sub(r"#.+?#", " ", text)
        # 将at替换为空格
        text = re.sub(r"@.*?\s", " ", text)
        # 保留中文和英文
        pattern = re.compile(u"[^0-9a-zA-Z\u4e00-\u9fa5]+", re.UNICODE)
        return pattern.sub(" ", text)
    
    def preprocess(self):
        if os.path.exists(self.save_weibo_file):
            return
        result = {}
        with open(self.raw_weibo_file, "r", encoding="utf-8") as inf:
            next(inf)
            csv_reader = csv.reader(inf)
            for line in csv_reader:
                idx = line[0]
                text = self.__clear_text(line[4]) + self.__clear_text(line[5])
                result[idx] = text
        with open(self.save_weibo_file, "w", encoding="utf-8") as outf:
            json.dump(result, outf, ensure_ascii=False)


class LDAModel(object):
    def __init__(self, raw_weibo_file, save_weibo_file, stop_word_file, new_stop_words=[], new_jieba_words=[]):
        WeiboPreprocess(raw_weibo_file, save_weibo_file).preprocess()
        self.weibo_text_file = save_weibo_file
        with open(stop_word_file, "r", encoding="utf-8") as f:
            self.stop_words = [line.strip() for line in f.readlines()]
        self.stop_words.extend(new_stop_words)

        for word in new_jieba_words:
            jieba.add_word(word)
        pass
    
    def __cut_word(self, text, if_flag=True):
        # 分词
        if not if_flag:
            words = [x.word for x in jp.cut(text)]
        else:
            words = []
            allowed_flags = ["n", "nr", "ns", "nt", "nz", "s", "t", "v", "vd", "vn", "an", "eng"]
            for word in jp.cut(text):
                if word.flag in allowed_flags:
                    words.append(word.word)
        # 去除停用词
        words = [x for x in words if x not in self.stop_words]
        return words
    
    def lda(self, save_dir, num_topics=6, if_flag=False):
        for filename in os.listdir(save_dir):
            os.remove(os.path.join(save_dir, filename))
        
        with open(self.weibo_text_file, "r", encoding="utf-8") as inf:
            obj = json.load(inf)
        documents = list(obj.values())
        document_keys = list(obj.keys())
        
        docs = [self.__cut_word(doc, if_flag) for doc in documents]
        dictionary = corpora.Dictionary(docs)
        corpus = [dictionary.doc2bow(doc) for doc in docs]
        lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
        
        # d = pyLDAvis.gensim_models.prepare(lda, corpus, dictionary)
        # pyLDAvis.show(d, local=False)

        # 打印每个类别最有关系的五个词汇
        for topic in lda.print_topics(num_words=10):
            print(topic)

        infer = lda.inference(corpus)[0]

        # 推断语料库的类别
        for idx, values in enumerate(infer):
            topic_val = 0
            topic_id = 0
            for tid, val in enumerate(values):
                if val > topic_val:
                    topic_val = val
                    topic_id = tid
            with open(os.path.join(save_dir, "topic{}.txt".format(topic_id)), "a", encoding="utf-8") as f:
                f.write("%s\t%s\n" % (document_keys[idx], documents[idx]))

def main(raw_weibo_file, save_weibo_file, stop_word_file, save_dir, time_upper_bound, time_lower_bound):
    new_stop_words = [" ", "微博", "王一博", "月", "日", "转发", "请", "http", "cn", "武汉", "疫情", "中国", "会", "2020", "wyb", "新型", "实时"]
    new_jieba_words = ["王一博", "王俊凯", "微博", "战疫"]

    '''
        删选时段
    '''
    time_lower_bound = datetime.strptime(time_lower_bound, "%Y/%m/%d %H:%M:%S")
    time_upper_bound = datetime.strptime(time_upper_bound, "%Y/%m/%d %H:%M:%S")
    if not os.path.isdir("./tmp"):
        os.mkdir("./tmp")
    newWeiboFile = "./tmp/weibo.csv"
    with open(raw_weibo_file, "r", encoding="utf-8") as inf, open(newWeiboFile, "w", encoding="utf-8", newline="") as outf:
        line = inf.readline()
        outf.write(line)
        csv_reader = csv.reader(inf)
        csv_writer = csv.writer(outf)
        for line in csv_reader:
            try:
                t = datetime.strptime(line[3], "%Y/%m/%d %H:%M:%S")
            except ValueError:
                t = datetime.strptime(line[3], "%Y-%m-%d %H:%M:%S")
            if time_lower_bound <= t and t <= time_upper_bound:
                csv_writer.writerow(line)
    
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    LDA = LDAModel(newWeiboFile, save_weibo_file, stop_word_file, new_stop_words, new_jieba_words)
    LDA.lda(save_dir=save_dir, num_topics=3)

if __name__ == "__main__":
    times = ["0120", "0220", "0317", "0428", "0918"]
    stop_word_file = "../data/stop_words.txt"
    raw_weibo_file = "../data/weibo.csv"
    for i in range(len(times)):
        for j in range(i + 1, len(times)):
            print("ldaing for time zone [{}, {}]".format(times[i], times[j]))
            time_lower_bound = "2020/{}/{} 00:00:00".format(times[i][:2], times[i][2:])
            time_upper_bound = "2020/{}/{} 00:00:00".format(times[j][:2], times[j][2:])
            save_weibo_file = "../result/weibo_text_from_{}_to_{}.json".format(times[i], times[j])
            save_dir = "../result/lda_from_{}_to_{}".format(times[i], times[j])
            main(raw_weibo_file, save_weibo_file, stop_word_file, save_dir, time_upper_bound, time_lower_bound)