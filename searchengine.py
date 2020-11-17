from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import os
from utils import maps, query_template
import gc
import tqdm
import json

class SearchEngine:
    def __init__(self, index_name="sogou-corpus"):
        self.es = Elasticsearch()
        self.index_name = index_name
        self.sentence_id = 0
        self.init()
            
    def init(self):
        if not self.es.indices.exists(index=self.index_name):
            result = self.es.indices.create(index=self.index_name, ignore=[400, 404], body = maps)
            print('Create index {}.'.format(self.index_name))
        else:
            print('Find index {}. So don\'t create a new one.'.format(self.index_name))

    def build_index_by_file(self, filename):
        sen_list = []
        with open(filename, encoding='utf-8') as f:
            for line in tqdm.tqdm(f, desc='build index for {}'.format(filename.split('/')[-1])):
                line = line.strip()
                if len(line) < 1:
                    continue
                linesplit = line.split(' ')
                word_list, pos_list = self.parse(linesplit)
                sen_list.append([word_list, pos_list, self.sentence_id])
                self.sentence_id += 1
                if self.sentence_id % 20000 == 0:
                    self.insert_sen(sen_list)
                    del sen_list
                    gc.collect()
                    sen_list = []
    
    def insert_sen(self, sen_list):
        content = ({
            "_index":self.index_name,
            "_source": {
                "text":each[0], "pos":each[1]
            },
            "_id": each[2]
        } for each in sen_list)
        helpers.bulk(self.es, content)

    def parse(self, linesplit):
        word_list = []
        pos_list = []
        for item in linesplit:
            try:
                word, pos = item.split('_')
                word_list.append(word)
                pos_list.append(pos)
            except:
                continue
        return word_list, pos_list

    def build_index_by_dir(self, corpus_dir):
        for files in os.listdir(corpus_dir):
            filename = os.path.join(corpus_dir, files)
            self.build_index_by_file(filename)

    def delete_index(self, index_name):
        self.es.indices.delete(index=index_name)

    def query(self, keywords, size=1000):
        query = json.loads(json.dumps(query_template))
        for keyword in keywords:
            query['query']['bool']['must'].append({'match': {'text' : keyword}})
        res = self.es.search(index=self.index_name, body=query, size=size)
        res = res['hits']['hits']
        sen_list = []
        pos_list = []
        for item in res:
            sen_list.append(item['_source']['text'])
            pos_list.append(item['_source']['pos'])
        return sen_list, pos_list

if __name__ == "__main__":
    '''
    se = SearchEngine()
    
    se.build_index_by_file("/data/disk2/private/hujinyi/IRsystem/corpus_cut/Sogou0012_cut.txt")
    se.build_index_by_file("/data/disk2/private/hujinyi/IRsystem/corpus_cut/Sogou0013_cut.txt")
    se.build_index_by_file("/data/disk2/private/hujinyi/IRsystem/corpus_cut/Sogou0014_cut.txt")
    '''