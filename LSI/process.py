import tqdm
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

class LSI():
    def __init__(self, corpus_path, stopwords_path):
        self.corpus_path = corpus_path
        self.stopwords_path = stopwords_path
        self.load_stopwords()
        #self.load_sentence()

    def load_stopwords(self):
        words = []
        with open(self.corpus_path, encoding='utf-8') as f:
            for line in f:
                words.append(line.strip())
        self.stopwords_list = words

    def load_sentence(self):
        sentence = []
        words = []
        with open(self.corpus_path, encoding='utf-8') as f:
            for line in tqdm.tqdm(f):
                line = line.strip().split(' ')
                sen = self.filter(line)
                if len(sen) == 0:
                    continue
                sentence.append(sen)
                words.extend(sen)
        self.sentence_list = sentence
        self.word_list = list(set(words))
    
    def _is_chinese_char(self, char):
        cp = ord(char)
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
            (cp >= 0x3400 and cp <= 0x4DBF) or  #
            (cp >= 0x20000 and cp <= 0x2A6DF) or  #
            (cp >= 0x2A700 and cp <= 0x2B73F) or  #
            (cp >= 0x2B740 and cp <= 0x2B81F) or  #
            (cp >= 0x2B820 and cp <= 0x2CEAF) or
            (cp >= 0xF900 and cp <= 0xFAFF) or  #
            (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
            return True

        return False

    def _is_chinese_word(self, word):
        for char in word:
            if not self._is_chinese_char(char):
                return False
        
        return True

    def filter(self, word_list):
        ans = []
        for word in word_list:
            if word in self.stopwords_list:
                continue
            if not self._is_chinese_word(word):
                continue
            ans.append(word)
        return ans
    
    def build_term_doc(self):
        ans = []
        for word in tqdm.tqdm(self.word_list):
            temp = []
            for sen in self.sentence_list:
                temp.append(sen.count(word))
            ans.append(temp)
        ans = np.array(ans)
        return ans
        
    def reduce_dimension(self, k, matrix):
        svd = TruncatedSVD(n_components=k)
        ans = svd.fit_transform(matrix)
        return ans

    def build_term_term(self, window_size=5):
        self.word2index = {word:index for index, word in enumerate(self.word_list)}
        term_term_matrix = np.zeros((len(self.word_list), len(self.word_list)))
        for sen in self.sentence_list:
            slide = min(window_size, len(sen))
            first_word_index = self.word2index[sen[0]]
            for i in range(1, slide):
                current_word_index = self.word2index[sen[i]]
                term_term_matrix[first_word_index, current_word_index] += 1
                term_term_matrix[current_word_index, first_word_index] += 1
            if slide < len(sen):
                for i in range(1, len(sen) - slide):
                    first_word_index = self.word2index[sen[i]]
                    second_word_index = self.word2index[sen[i + slide]]
                    term_term_matrix[first_word_index, second_word_index] += 1
                    term_term_matrix[second_word_index, first_word_index] += 1
        return term_term_matrix
    
    def compute_fre(self):
        word2fre = {}
        for sen in self.sentence_list:
            for word in sen:
                if word in word2fre:
                    word2fre[word] += 1
                else:
                    word2fre[word] = 1
        return word2fre

    def plot1(self, minrange=1, maxrange=300):
        try:
            initial_matrix = np.load("term_doc.npy")
        except:
            initial_matrix = self.build_term_doc()
        initial_norm = np.linalg.norm(initial_matrix)
        value_list = []
        for k in tqdm.trange(minrange, maxrange):
            ans = self.reduce_dimension(k, initial_matrix)
            norm = np.linalg.norm(ans)
            value_list.append(initial_norm / norm)
        plt.plot(range(minrange, maxrange), value_list)
        plt.title("The variation of similarity with the change of k")
        plt.xlabel("k")
        plt.ylabel("similarity")
        plt.savefig("prob1.png")
        plt.close()

    def plot2_complete(self, k):
        try:
            initial_matrix = np.load("term_doc.npy")
        except:
            initial_matrix = self.build_term_doc()
        word_embedding = self.reduce_dimension(k, initial_matrix)
        doc_embedding = self.reduce_dimension(k, initial_matrix.transpose(1, 0))
        tsne = TSNE(n_components=2, verbose=1)
        word_view = tsne.fit_transform(word_embedding)
        doc_view = tsne.fit_transform(doc_embedding)
        np.save("word_view.npy", word_view)
        np.save("doc_view.npy", doc_view)
        plt.scatter(word_view[:, 0], word_view[:, 1], s=10, label="word embedding")
        plt.scatter(doc_view[:, 0], doc_view[:, 1], s=10, label="doc embedding")
        plt.legend()
        plt.savefig("prob_complete_k_{}.png".format(k))
        plt.close()

    def plot2_highf(self, k, topk=100):
        try:
            initial_matrix = np.load("term_doc.npy")
        except:
            initial_matrix = self.build_term_doc()
        word_embedding = self.reduce_dimension(k, initial_matrix)
        word2fre = self.compute_fre()
        sorted_word2fre = sorted(word2fre.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
        top_word = [item[0] for index, item in enumerate(sorted_word2fre) if index < topk]
        top_word_index = [self.word2index[word] for word in top_word]
        top_word_embedding = word_embedding[top_word_index, :]
        tsne = TSNE(n_components=2, verbose=1)
        word_view = tsne.fit_transform(top_word_embedding)
        plt.scatter(word_view[:, 0], word_view[:, 1], s=10, label="top word embedding")
        plt.legend()
        plt.savefig("prob_top_word_k_{}.png".format(k))
        plt.close()

corpus_path = "/data/disk2/private/hujinyi/IRHomework/corpus/renminribao_cut.txt"
stopwords_path = "/data/disk2/private/hujinyi/IRHomework/cache/stop_words.txt"
lsi = LSI(corpus_path, stopwords_path)
#lsi.plot2(k=100)
#term_term_5 = lsi.build_term_term(window_size=5)
#np.save('term_term_5.npy', term_term_5)
#ans = lsi.build_term_doc()
#
#plot1(lsi, term_doc)

word_view = np.load("word_view.npy")
doc_view = np.load("doc_view.npy")
plt.scatter(word_view[:, 0], word_view[:, 1], s=10, label="word embedding")
plt.scatter(doc_view[:, 0], doc_view[:, 1], s=10, label="doc embedding")
plt.legend()
plt.savefig("k100.png")