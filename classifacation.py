import inline
import matplotlib
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
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import warnings

from db_conn import cursor

# goodArticles = []
# goodTitles = []
# goodAnnotations = []
# badArticles = []
# badTitles = []
# badAnnotations = []
# 
# cursor.execute('select * from articles where status=true')
# mobile_records = cursor.fetchall()
# 
# for row in mobile_records:
#     goodTitles.append(row[0])
# 
# cursor.execute('select * from articles where status=false')
# mobile_records = cursor.fetchall()
# 
# for row in mobile_records:
#     badTitles.append(row)
# 
# cursor.execute('select count(*) from articles')
# mobile_records = cursor.fetchall()
# count = mobile_records[0][0]

url = 'https://api.pushshift.io/reddit/search/submission/?subreddit=fantasy'
url2 = 'https://api.pushshift.io/reddit/search/submission/?subreddit=sciencefiction'
res = requests.get(url + '&size=1000&fields=body,title,author,permalink,url')
res2 = requests.get(url2 + '&size=1000&fields=body,title,author,permalink,url')
print(res.status_code)
print(res2.status_code)

fantasy = res.json()['data']
sciencefiction = res2.json()['data']
fan = pd.DataFrame(fantasy)
sf = pd.DataFrame(sciencefiction)
fan['subreddit_target'] = 0
sf['subreddit_target'] = 1
fan['subreddit'] = 'fan'
sf['subreddit'] = 'sf'
df_list = [fan, sf]
df = pd.concat(df_list).reset_index(drop=True)
print(df)
def tokenize(x):
    tokenizer = RegexpTokenizer(r'\w+')
    return tokenizer.tokenize(x)
df['tokens'] = df['title'].map(tokenize)