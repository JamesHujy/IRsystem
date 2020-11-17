import thulac
import tqdm
import json
thul = thulac.thulac()

word_dict = {}

def count_file(filename):
    with open(filename) as f:
        for line in tqdm.tqdm(f):
            line = line.strip()
            word_list = line.split(' ')
            for word in word_list:
                try:
                    word, pos = word.split("_")
                except:
                    continue
                if word in word_dict:
                    if pos in word_dict[word]:
                        word_dict[word][pos] += 1
                    else:
                        word_dict[word][pos] = 1
                else:
                    word_dict[word] = {}
                    if pos in word_dict[word]:
                        word_dict[word][pos] += 1
                    else:
                        word_dict[word][pos] = 1
                        
def cut_file(filename):
    ans_list = []
    with open(filename) as f:
        for line in tqdm.tqdm(f):
            line = line.strip()
            line = line.replace("<N>", "")
            line = line.replace(" ", "")
            ans_list.append(line)
    with open(filename+'_nospace.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ans_list))
    #thul.cut_f(filename+'_nospace.txt', filename+'_cut.txt')
'''       
filename="./corpus/Sogou0000"
cut_file(filename)
filename="./corpus/Sogou0010"
cut_file(filename)
filename="./corpus/Sogou0011"
cut_file(filename)
filename="./corpus/Sogou0012"
cut_file(filename)
filename="./corpus/Sogou0013"
cut_file(filename)

filename="./corpus_cut/Sogou0000_cut.txt"
count_file(filename)
filename="./corpus_cut/Sogou0010_cut.txt"
count_file(filename)
filename="./corpus_cut/Sogou0011_cut.txt"
count_file(filename)
filename="./corpus_cut/Sogou0012_cut.txt"
count_file(filename)
filename="./corpus_cut/Sogou0013_cut.txt"
count_file(filename)
filename="./corpus_cut/Sogou0014_cut.txt"
count_file(filename)

with open('word_to_pos_count.json', 'w') as f:
    json.dump(word_dict, f, indent=2)

'''
with open('./cache/word_to_pos_count.json') as f:
    word_dict = json.load(f)
for word, count in word_dict.items():
    max_count = max(count.values())
    temp_dict = []
    for pos, cnt in count.items():
        if cnt > max_count / 100:
            temp_dict.append(pos)
    word_dict[word] = temp_dict

with open('word_to_pos_count2.json', 'w') as f:
    json.dump(word_dict, f, indent=2)