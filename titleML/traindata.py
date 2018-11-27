import jieba
import csv
import pandas as pd
from util.readtext import read_userdict, read_excel
def getStopWords(path):
    stopwords = pd.read_csv('%s%s' % (path, 'stopword.txt'), index_col=False,quoting=3, sep="\t", names=['stopword'], encoding='utf-8')
    stopwords = stopwords["stopword"].values
    return stopwords
def get_user_list():
    rule_dict_f, rule_dict_fa, rule_dict_other, rule_dict_title, rule_dict_gate = read_excel('data/regular.xlsx')
    # 读取自定义词典
    custom_words, lines = read_userdict('data/userdict.txt', rule_dict_other)
    jieba.load_userlist(lines)
def preprocess_text(line,stopwords):
    try:
        segs=jieba.lcut(line)                                       # 利用结巴分词进行中文分词
        segs = [v for v in segs if not str(v).isdigit()]            # 去数字
        segs = list(filter(lambda x: x.strip(), segs))              # 去左右空格
        segs = list(filter(lambda x: len(x) > 1, segs))             # 去掉长度小于1的词
        segs = list(filter(lambda x: x not in stopwords, segs))     # 去掉停用词
        return " ".join(segs)               # 把当前的文本和对应的类别拼接起来，组合成fasttext的文本格式
    except Exception as e:
        print(line, e)

def new_csv(sentence, path_csv, type):
    if type == 1:
        path_csv += 'y.csv'
    if type == 2:
        path_csv += 'n.csv'
    try:
        with open(path_csv, 'a', encoding='utf-8', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, dialect='excel')
            csv_writer.writerow(sentence)
    except Exception as e:
            print(e)

def add_new_data(sentence, type, path_csv):
    stop_words = getStopWords(path_csv)
    sentence = preprocess_text(sentence, stop_words)
    if type == 1:
        path_csv += 'y.csv'
    if type == 2:
        path_csv += 'n.csv'
    try:
        with open(path_csv, 'a', encoding='utf-8', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, dialect='excel')
            csv_writer.writerow(sentence)
    except Exception as e:
            print(e)

if __name__ == "__main__":
    get_user_list()
    add_new_data('项目类型：货物类（含药品集中采购）项目编号：BGZJ－ZC17572－2', 2, 'data/')
