import numpy
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix, f1_score
import sys
import tablemagician
from os.path import join
import pickle

 
def build_data_frame(train_sets):
    rows = []
    index = []
    for classification in train_sets:
        for column in train_sets[classification]:
            col_string = ' '.join([str(c.value) for c in column['values'] if c.value])
            rows.append({'text': col_string, 'class': classification})
            index.append(column['name'])
 
    data_frame = DataFrame(rows, index=index)
    return data_frame


if __name__ == '__main__':
    path = sys.argv[1]
    headers = sys.argv[2:]

    train_sets = {}
    for h in headers:
        with open(join(path, h + '.pkl'), 'rb') as handle:
            train_sets[h] = pickle.load(handle)

    data = build_data_frame(train_sets)
    data = data.reindex(numpy.random.permutation(data.index))
    pipeline = Pipeline([
        ('count_vectorizer',   CountVectorizer(ngram_range=(1, 2))),
        ('classifier',         MultinomialNB())
    ])
    pipeline.fit(data['text'].values, data['class'].values)

    # build example data
    dts = tablemagician.from_path('/home/sebastian/Repositories/csvprofiler/parser/testdata/nuts/4659.csv')
    for dt in dts:
        at = dt.process(max_lines=100)
        col_str = ' '.join([str(c.value) for c in at.columns[at.headers.index('SEX')] if c.value])
        print col_str

    predictions = pipeline.predict([col_str])
    print 'prediction'
    print predictions # [1, 0]