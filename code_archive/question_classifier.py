import sqlite3
import re
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import precision_score,recall_score, accuracy_score, classification_report

import pandas as pd

def vectorize(row,features):
    # empty vector
    vector = []

    # create custom feature vector with label
    for feature in features:

        # match against the feature
        match = re.search(feature, row[0].lower())

        if match is not None:
            vector.extend([1])
        else:
            vector.extend([0])

    # extend the label
    vector.append(row[1])

    return vector

where_features =['where is','where are','where can','where was','where you','where']
who_features = ['who is','who was','who are','who were','who to','who did','who do','who']
what_features = ['what is','what was','what are','what were','what to','what did','what do','what']
when_features = ['when is','when was','when are','when were','when to','when did','when do','when']
why_features = ['why is','why was','why are','why were','why did','why do','why']
which_features = ['which is','which was','which are','which were','which did','which do','which']
how_features = ['how is','how was','how are','how were','how did','how do','how']
# qm = ['hello']
qm =['\?']

features = where_features + who_features + \
           what_features + when_features + why_features + which_features + \
           how_features + qm

stmt_sql = "select distinct stmt, 'statement' as label  from stmts where " \
           "(stmt like '% where %' or stmt  like '% who %' " \
           "or stmt like '% what %'  or stmt like '% when %'  " \
           "or stmt like '% why %') " \
           "and (stmt not like '%?%')"

qn_sql = "select distinct stmt, 'question' as label  from stmts where " \
           "(stmt like '% where %' or stmt  like '% who %' " \
           "or stmt like '% what %'  or stmt like '% when %'  " \
           "or stmt like '% why %') " \
           "and (stmt like '%?%')"

db_path = '../../database/jiakbot.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# create empty data set
data = []

# get the stmts
for row in c.execute(stmt_sql):
    vector = vectorize(row,features)
    data.append(vector)

for row in c.execute(qn_sql):
    vector = vectorize(row, features)
    data.append(vector)

df = pd.DataFrame(data)
df.rename(columns={52:'label'}, inplace=True)

strat_split = StratifiedShuffleSplit(n_splits=1, train_size=0.75, test_size=0.25, random_state=2016)

for train_index, test_index in strat_split.split(df,df.iloc[:,-1]):
    df_train, df_test = df.ix[train_index], df.ix[test_index]
    print('Size of data set: ', len(df))
    print('Size of training data set: ', len(train_index))

print('Verifying distribution ...')
train_table = df_train.rename(index=str, columns={'label':'training_count'})
test_table = df_test.rename(index=str, columns={'label':'test_count'})
verify = pd.concat([train_table.ix[:,51:].groupby('training_count').count(),
                    test_table.ix[:, 51:].groupby('test_count').count()],axis = 1)

features_train = df_train.ix[:,:-1]
label_train = df_train.ix[:,-1]

print('Fitting model to predict question statements ...')
clf = MultinomialNB()
clf.fit(features_train, label_train)

predicted_label_train = clf.predict(features_train)

features_test = df_test.ix[:,:-1]
label_test = df_test.ix[:,-1]

print('Predicting question statement labels ... ')
predicted_label_test = clf.predict(features_test)

precision_train = precision_score(label_train, predicted_label_train, average='weighted')
recall_train = recall_score(label_train, predicted_label_train, average='weighted')
accuracy_train = accuracy_score(label_train, predicted_label_train)

precision_test = precision_score(label_test, predicted_label_test, average='weighted')
recall_test = recall_score(label_test, predicted_label_test, average='weighted')
accuracy_test = accuracy_score(label_test, predicted_label_test)

print('---------------------------------------')
print('training results ... ')
print('precision :', precision_train)
print('recall :', recall_train)
print('accuracy :', accuracy_train)

print('test results ... ')
print('precision :', precision_test)
print('recall :', recall_test)
print('accuracy :', accuracy_test)
print('---------------------------------------')