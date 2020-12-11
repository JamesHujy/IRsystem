from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from io import BytesIO
import json
from searchengine import SearchEngine
from retriever import Retriever
from transformers import BertTokenizer, BertModel
from ranker import BertRanker, Word2vecRanker

app = Flask(__name__)
cors = CORS(app, resources={r'/get': {"origins": "*"}})
se = SearchEngine()

with open('../cache/word_to_pos_count2.json') as f:
    word_to_pos = json.load(f)
with open('../cache/pos_hanzi.json') as f:
    pos_to_hanzi = json.load(f)
hanzi_to_pos = {hanzi:pos for pos, hanzi in pos_to_hanzi.items()}
hanzi_to_pos['不限'] = 'all'
print('finish load...')
initialPos = ['名词', '人名', '地名', '机构名', '其它专名', '数词', '量词', '数量词', '时间词', '方位词', '处所词', '动词', '形容词', '副词', '前接成分', '后接成分', '习语', '简称', '代词', '连词', '介词', '助词', '语气助词', '叹词', '拟声词', '语素', '标点', '其它']
bert = BertModel.from_pretrained("hfl/chinese-bert-wwm-ext")
tokenizer = BertTokenizer.from_pretrained("hfl/chinese-bert-wwm-ext")
bertranker = BertRanker()
word2vecranker = Word2vecRanker("/data/disk2/private/hujinyi/IRHomework/cache/sgns.renmin.word")

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/get', methods=['GET', 'POST'])
def getData():
    types = request.args.get('type')
    if types == '1':
        words = request.args.get('words')
        if len(words) == 0:
            response = initialPos
        else:
            pos = word_to_pos[words]
            pos = [pos_to_hanzi[each] for each in pos]
            response = pos
        return jsonify(response)
    else:
        choice_list = ['bert', 'word2vec', 'none']
        choice_index = int(request.args.get('choice'))
        choice = choice_list[choice_index]

        query_list = request.args.get('words').split(',')
        sen_list, ans_pos_list = se.query([each for each in query_list if len(each) > 0])
        pos_list = request.args.get('posList').split(',')
        pos_list = [hanzi_to_pos[each] for each in pos_list]
        relative_list = request.args.get('relative').split(',')
        relativeObject_list = request.args.get('relativeObject').split(',')
        re = Retriever(sen_list, query_list, pos_list_document=ans_pos_list, pos_list_query=pos_list, relative=relative_list, relativeObject=relativeObject_list)
        response = re.rank()
        if list(set(pos_list)) != ['all']:
            response = re.filter_by_pos()
        if list(set(relative_list)) != ['不限']:
            response = re.filter_relative()
        response = ["".join(each) for each in response]
        if choice == 'none':
            return jsonify(response[:50])
        elif choice == 'bert':
            new_sen = bertranker.rank(query_list, response[:50])
            return jsonify(new_sen)
        else:
            new_sen = word2vecranker.rank(query_list, response[:50])
            return jsonify(new_sen)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12306)
