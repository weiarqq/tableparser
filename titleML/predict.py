import numpy as np
import pandas as pd
import jieba
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.externals import joblib
from util.readtext import read_userdict,read_excel
def get_user_list():
    rule_dict_f, rule_dict_fa, rule_dict_other, rule_dict_title, rule_dict_gate = read_excel('data/regular.xlsx')
    # 读取自定义词典
    custom_words, lines = read_userdict('data/userdict.txt', rule_dict_other)
    jieba.load_userlist(lines)
def loadfacData(path_csv):
    df_factor = pd.read_csv(path_csv,encoding="utf-8")
    df_factor = df_factor.dropna()
    df_factor = np.array(df_factor)
    factor = []  # list
    for t in df_factor.tolist():
        factor.append(t[0])
    return factor
def loadData():
    data_path ="D:\\resultBid\\"
    #利用pandas把数据读进来
    test = loadfacData(data_path+"test.csv")
    return test
def preprocess_text(line,sentences,stopwords):
        try:
            segs = jieba.lcut(line)    #利用结巴分词进行中文分词
            segs = [v for v in segs if not str(v).isdigit()]#去数字
            segs = list(filter(lambda x: x.strip(), segs))  # 去左右空格
            segs = list(filter(lambda x: len(x) > 1, segs))    #去掉长度小于1的词
            segs = list(filter(lambda x: x not in stopwords, segs))   #去掉停用词
            sentences.append(" ".join(segs))   #把当前的文本和对应的类别拼接起来，组合成fasttext的文本格式
        except Exception:
            print(line)
def getStopWords(datapath):
    stopwords=pd.read_csv(datapath,index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')
    stopwords=stopwords["stopword"].values
    return stopwords
def predict_TITLE(text, path):
    # 加载分类器
    clf = joblib.load('%s%s' % (path, 'model/model.pkl'))
    count_vect = joblib.load('%s%s' % (path, 'model/count_vect'))
    sentences = []
    stopwords = getStopWords('%s%s' % (path, "data/stopword.txt"))
    preprocess_text(text, sentences, stopwords)
    tfidf_transformer = TfidfTransformer()
    for sentence in sentences:
        X_new_counts = count_vect.transform([sentence])
        X_new_tfidf = tfidf_transformer.fit_transform(X_new_counts)
        # 进行预测
        predicted = clf.predict(X_new_tfidf)
        print(predicted)
        print('-------------------------------'+sentence)

if __name__ == '__main__':
    get_user_list()
    predict_TITLE('项目类型：货物类（含药品集中采购）项目编号：BGZJ－ZC17572－2','')
    '项目 类型 货物 药品 集中采购 项目编号 BGZJ ZC17572'

