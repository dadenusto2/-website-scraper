import inline
import matplotlib
import nltk
import pandas as pd
import numpy as np
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.tokenize import RegexpTokenizer
from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import warnings
import json
from db_conn import cursor

nltk.download('wordnet')


cursor.execute('select * from articles where status=true')
results = []
columns = (
    'title', 'authors', 'anatation', 'text', 'tags', 'status'
)
for row in cursor.fetchall():
    results.append(dict(zip(columns, row)))
df_list = json.dumps(results, indent=2)
tr = pd.DataFrame(eval(df_list.replace('true', 'True')))

cursor.execute('select * from articles where status=false')
results = []
columns = (
    'title', 'authors', 'anatation', 'text', 'tags', 'status'
)
for row in cursor.fetchall():
    results.append(dict(zip(columns, row)))
df_list = json.dumps(results, indent=2)
fl = pd.DataFrame(eval(df_list.replace('false', 'False')))
df = pd.concat([tr, fl]).reset_index(drop=True)

def tokenize(x):
    tokenizer = RegexpTokenizer(r'\w+')
    return tokenizer.tokenize(x)

search_field = 'tags'
df['tokens'] = df[search_field].map(tokenize)


def stemmer(x):
    stemmer = PorterStemmer()
    return ' '.join([stemmer.stem(word) for word in x])


def lemmatize(x):
    lemmatizer = WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word) for word in x])


df[search_field] = df['tokens'].map(lemmatize)
df['tags'] = df['tokens'].map(stemmer)

X = df[search_field]
y = df['status']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

pipe_mnnb = Pipeline(steps = [('tf', TfidfVectorizer()), ('mnnb', MultinomialNB())])

pgrid_mnnb = {
 'tf__max_features' : [1000, 2000, 3000],
 # 'tf__stop_words' : None,
 'tf__ngram_range' : [(1,1),(1,2)],
 'tf__use_idf' : [True, False],
 'mnnb__alpha' : [0.1, 0.5, 1]
}

gs_mnnb = GridSearchCV(pipe_mnnb, pgrid_mnnb, cv=5, n_jobs=-1)
gs_mnnb.fit(X_train, y_train)

gs_mnnb.score(X_train, y_train)
gs_mnnb.score(X_test, y_test)

gs_mnnb.best_params_

preds_mnnb = gs_mnnb.predict(X)
df['preds'] = preds_mnnb

conf_mnnb = confusion_matrix(y_test, preds_mnnb[0:len(y_test)])
print(conf_mnnb)
