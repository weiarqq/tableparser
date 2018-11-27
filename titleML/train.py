import jieba
# jieba.load_userdict("./data/userdict.txt")
import numpy as np
from sklearn.externals import joblib
import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split

def loadfacData(path_csv):
    df_factor = pd.read_csv(path_csv, encoding="utf-8")
    df_factor = df_factor.dropna()
    df_factor = np.array(df_factor)
    factor = []  # list
    for t in df_factor.tolist():
        factor.append(t[0])
    return factor
def loadData(data_path):
    title_y = loadfacData(data_path+'y.csv')
    title_n = loadfacData(data_path+'n.csv')
    return title_y, title_n

def preprocess_text(content_line,sentences,category):
    for line in content_line:
        sentences.append((line, category))
def getStopWords(datapath):
    stopwords = pd.read_csv(datapath,index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')
    stopwords = stopwords["stopword"].values
    return stopwords

def train_TITLE(path):
    title_y, title_n = loadData(path)
    sentences = []
    preprocess_text(title_y, sentences, 1)
    preprocess_text(title_n, sentences, 2)
    random.shuffle(sentences)  # 做乱序处理,使得同类别的样本不至于扎堆
    x, y = zip(*sentences)
    print(1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1234)  # 划分训练集和测试集
    print('reading training and testing data...')
    vec = CountVectorizer(analyzer='word', ngram_range=(1, 2), max_features=10000)
    tf = TfidfTransformer()
    x_train = vec.fit_transform(x_train)
    x_train_tf = tf.fit_transform(x_train)
    from sklearn.naive_bayes import MultinomialNB
    model = MultinomialNB(alpha=0.01)
    nb = model.fit(x_train_tf, y_train)
    joblib.dump(nb, 'model.pkl')
    joblib.dump(vec, 'count_vect')

if __name__ == "__main__":
    train_TITLE('data/')
