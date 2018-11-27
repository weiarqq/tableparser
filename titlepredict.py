from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfTransformer
import pandas as pd
import jieba
class PredictTitle():
    def __init__(self):
        self.stopwords = []
        self.packages = []
        self.clf = joblib.load('titleML/model/model.pkl')
        self.count_vect = joblib.load('titleML/model/count_vect')
    def init(self, pags):
        self.packages = pags
        self.stopwords = pd.read_csv('titleML/data/stopword.txt', index_col=False, quoting=3, sep="\t", names=['stopword'], encoding='utf-8')["stopword"].values
    def is_title(self, rows_list):
        num = 0
        for row in rows_list:
            if row is not None and row !='' and row !='无':
                num += 1
        if num < 2:
            return 0
        rows_string = ''.join(rows_list)
        if rows_string is None:
            return 0
        rows_string = ''.join(rows_string.split())
        if len(rows_string) <= 0:
            return 0
        sentence, is_package = self.preprocess_text(rows_string, self.stopwords, self.packages)
        tfidf_transformer = TfidfTransformer()
        x_new_counts = self.count_vect.transform([sentence])
        x_new_tfidf = tfidf_transformer.fit_transform(x_new_counts)
        # 进行预测
        predicted = self.clf.predict(x_new_tfidf)
        if predicted[0] == 2:
            return 0
        elif is_package == 1:
            return 1
        else:
            return 2

    def preprocess_text(self, content_line, stopwords, packages):
        try:

            segs = jieba.lcut(content_line)  # 利用结巴分词进行中文分词
            segs = [v for v in segs if not str(v).isdigit()]  # 去数字
            segs = list(filter(lambda x: x.strip(), segs))  # 去左右空格
            segs = list(filter(lambda x: len(x) > 1, segs))  # 去掉长度小于1的词
            segs = list(filter(lambda x: x not in stopwords, segs))  # 去掉停用词
            if len(segs) <= 0:
                return "", 0
            for seg in segs:
                if seg in packages:
                    return " ".join(segs), 1
            return " ".join(segs), 0  # 把当前的文本和对应的类别拼接起来，组合成fasttext的文本格式
        except Exception as e:
            print(e)