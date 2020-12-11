from transformers import BertModel
from transformers import BertTokenizer
import torch
import numpy as np
import jieba

class BertRanker():
    def __init__(self):
        self.bert = BertModel.from_pretrained("hfl/chinese-bert-wwm-ext")
        self.tokenizer = BertTokenizer.from_pretrained("hfl/chinese-bert-wwm-ext")
        self.tokenizer.do_basic_tokenize = False

    def get_rep(self, item_list):
        ans_list = []
        for item in item_list:
            inputs = self.tokenizer(item, return_tensors="pt")
            rep = self.bert(**inputs)
            rep = torch.mean(rep[0][:, 1:-1, :], dim=1)
            ans_list.append(rep[0])
        return ans_list

    def compute_sim(self, a, b):
        output = torch.cosine_similarity(a,b, dim=0).data.numpy()
        return output

    def rank(self, query, senten):
        query_rep = self.get_rep(query)
        senten_rep = self.get_rep(senten)
        sim = []
        for sen in senten_rep:
            temp_sim = np.array([self.compute_sim(sen, query) for query in query_rep])
            sim.append(np.mean(temp_sim))
        sim = np.array(sim)
        index = np.argsort(-sim)
        new_sen = [senten[idx] for idx in index]
        return new_sen

class Word2vecRanker():
    def __init__(self, path):
        self.path = path
        jieba.load_userdict("dicts.txt")
        try:
            self.load()
        except:
            self.write()

    def write(self):
        words = []
        vectors = []
        with open(self.path) as f:
            for index, line in enumerate(f):
                if index == 0:
                    continue
                line_split = line.strip().split(' ')
                word = line_split[0]
                vector = line_split[1:]
                vector = [float(item) for item in vector]
                vectors.append(vector)
                words.append(word)
        self.vectors = np.array(vectors)
        self.words2index = {word:index for index, word in enumerate(words)}
        self.words = words
        np.save("vector.npy", vectors)
        with open('dicts.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(words))

    def load(self):
        self.words = []
        with open("dicts.txt", encoding="utf-8") as f:
            for line in f:
                self.words.append(line.strip())
        self.words2index = {word:index for index, word in enumerate(self.words)}
        self.vectors = np.load("vector.npy")
    
    def get_rep(self, item_list):
        ans_list = []
        for item in item_list:
            item_cut = list(jieba.cut(item))
            index = [self.words2index[each] for each in item_cut]
            rep = self.vectors[index]
            rep = np.mean(rep, axis=0)
            ans_list.append(rep)
        return ans_list

    def compute_sim(self, vA, vB):
        cos = np.dot(vA, vB) / (np.sqrt(np.dot(vA,vA)) * np.sqrt(np.dot(vB,vB)))
        return cos

    def rank(self, query, senten):
        query_rep = self.get_rep(query)
        senten_rep = self.get_rep(senten)
        sim = []
        for sen in senten_rep:
            temp_sim = np.array([self.compute_sim(sen, query) for query in query_rep])
            sim.append(np.mean(temp_sim))
        sim = np.array(sim)
        index = np.argsort(-sim)
        new_sen = [senten[idx] for idx in index]
        return new_sen