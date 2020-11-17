    
from gensim.summarization import bm25
from searchengine import SearchEngine
import numpy as np
import tqdm

class Retriever:
    def __init__(self, document_list, keyword_list, pos_list_document=None, pos_list_query=None, relative=None, relativeObject=None):
        self.document_list = document_list
        self.keyword_list = keyword_list
        self.pos_list_document = pos_list_document
        if pos_list_query is not None:
            self.pos_list_query = {keyword:pos for keyword, pos in zip(self.keyword_list, pos_list_query)}
        else:
            pos_list_query = None
        self.relative_list = relative
        self.relativeObject_list = relativeObject

    def calPosScore(self):
        def calPosScore(temp_dict):
            score = 0
            for word in self.keyword_list:
                if len(temp_dict[word]) == 1 and temp_dict[word] == self.pos_list_query[word]:
                    score += 10
                elif self.pos_list_query[word] == 'all':
                    score += 10
                elif len(temp_dict[word]) > 1 and self.pos_list_query[word] in temp_dict[word]:
                    score += 5
            return score
        pos_score_list = []
        for document, pos_list in zip(self.document_list, self.pos_list_document):
            temp_dict = {}
            for keyword in self.keyword_list:
                temp_dict[keyword] = []
            for word, pos in zip(document, pos_list):
                if word in self.keyword_list:
                    temp_dict[word].append(pos)
            for keyword in self.keyword_list:
                temp_dict[keyword] = list(set(temp_dict[keyword]))
            pos_score_list.append(calPosScore(temp_dict))
        return pos_score_list

    def calBM25(self):
        bm25Model = bm25.BM25(self.document_list)
        scores = bm25Model.get_scores(self.keyword_list)
        return scores

    def rank(self):
        scores = self.calBM25()
        index_rank = np.argsort(-np.array(scores))
        new_sens_list = [self.document_list[i] for i in index_rank]
        new_pos_list = [self.pos_list_document[i] for i in index_rank]
        self.document_list = new_sens_list
        self.pos_list_document = new_pos_list
        return new_sens_list

    def filter_by_pos(self):
        ans = []
        ans_pos = []
        for document, pos_list in zip(self.document_list, self.pos_list_document):
            temp_dict = {}
            for keyword in self.keyword_list:
                temp_dict[keyword] = []
            for word, pos in zip(document, pos_list):
                if word in self.keyword_list:
                    temp_dict[word].append(pos)
            for keyword in self.keyword_list:
                temp_dict[keyword] = list(set(temp_dict[keyword]))
            flag = True
            for word in self.keyword_list:
                if not self.pos_list_query[word] in temp_dict[word] and self.pos_list_query[word] != 'all' and word != "":
                    flag = False
                    break
            if flag:
                ans.append(document)
                ans_pos.append(pos_list)
        self.document_list = ans
        self.pos_list_document = ans_pos
        return ans

    def filter_by_word(self, word):
        ans = []
        ans_pos = []
        for document, pos_list in zip(self.document_list, self.pos_list_document):
            if word in "".join(document):
                ans.append(document)
                ans_pos.append(pos_list)
        self.document_list = ans
        self.pos_list_document = ans_pos

    def filter_by_word_pos(self, word, pos, left=True):
        ans = []
        ans_pos = []
        for document, pos_list in zip(self.document_list, self.pos_list_document):
            index = document.index(word)
            if left:
                if pos_list[index + 1] == pos:
                    ans.append(document)
                    ans_pos.append(pos_list)
            else:
                if pos_list[index - 1] == pos:
                    ans.append(document)
                    ans_pos.append(pos_list)
        self.document_list = ans
        self.pos_list_document = ans_pos

    def filter_by_two_words(self, word1, word2):
        ans = []
        ans_pos = []
        for document, pos_list in zip(self.document_list, self.pos_list_document):
            index1 = document.index(word1)
            index2 = document.index(word2)
            if index1 < index2:
                ans.append(document)
                ans_pos.append(pos_list)
        self.document_list = ans
        self.pos_list_document = ans_pos

    def filter_relative(self):
        for keyword, relative, relativeObject in zip(self.keyword_list, self.relative_list, self.relativeObject_list):
            if relative == '不限':
                continue
            if relative == '左相邻':
                if keyword == "":
                    self.filter_by_word_pos(relativeObject, self.pos_list_query[keyword], left=True)
                else:
                    query = keyword + relativeObject
                    self.filter_by_word(query)
            elif relative == '右相邻':
                if keyword == "":
                    self.filter_by_word_pos(relativeObject, self.pos_list_query[keyword], left=False)
                else:
                    query = relativeObject + keyword
                    self.filter_by_word(query)
            elif relative == '靠左':
                self.filter_by_two_words(keyword, relativeObject)
            elif relative == '靠右':
                self.filter_by_two_words(relativeObject, keyword)
        return self.document_list

'''
query_list = ['经历']
query_pos = ['v']
se = SearchEngine()
ans_list, pos_list = se.query(query_list)
retriever = Retriever(ans_list, query_list, pos_list_document=pos_list, pos_list_query=query_pos)
ans1 = retriever.retrieve_no_restrict()
ans2 = retriever.retrieve_by_pos()
print(["".join(each) for each in ans1][:5])
print(["".join(each) for each in ans2][:5])
query_list = ['经历']
query_pos = ['n']
se = SearchEngine()
ans_list, pos_list = se.query(query_list)
retriever = Retriever(ans_list, query_list, pos_list_document=pos_list, pos_list_query=query_pos)
ans1 = retriever.retrieve_no_restrict()
ans2 = retriever.retrieve_by_pos()
print(["".join(each) for each in ans1][:5])
print(["".join(each) for each in ans2][:5])
'''