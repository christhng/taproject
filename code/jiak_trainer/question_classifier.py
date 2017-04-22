import re
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score,recall_score, accuracy_score, classification_report
from sklearn.externals import joblib

import pickle

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

where_features =['where is','where are','where can','where was','where you','where to','where']
who_features = ['who is','who was','who are','who were','who to','who did','who do','who']
what_features = ['what is','what was','what are','what were','what to','what did','what do','what']
when_features = ['when is','when was','when are','when were','when to','when did','when do','when']
why_features = ['why is','why was','why are','why were','why did','why do','why']
which_features = ['which is','which was','which are','which were','which did','which do','which']
how_features = ['how is','how was','how are','how were','how did','how do','how']
would_features = ['why would','would i','would you']
can_features = ['can you','could you','could i']
qm =['\\?']

features = where_features + who_features + \
           what_features + when_features + why_features + which_features + \
           how_features + would_features + can_features + qm

file_path = 'code/jiak_trainer/question_corpus.txt'

corpus = pd.read_table('question_corpus.txt', sep='\t',header = 0)
#corpus = pd.read_table(file_path, sep='\t',header = 0)
matrix = corpus.as_matrix()

# create empty data set
data = []

# get the corpus vectors
for row in matrix:
    vector = vectorize(row,features)
    vector.append(row[0])
    data.append(vector)

df = pd.DataFrame(data)

df.rename(columns={len(df.columns)-2:'label'}, inplace=True)

strat_split = StratifiedShuffleSplit(n_splits=1, train_size=0.75, test_size=0.25, random_state=2016)

for train_index, test_index in strat_split.split(df,df.loc[:,'label']):
    df_train, df_test = df.ix[train_index], df.ix[test_index]
    print('Size of data set: ', len(df))
    print('Size of training data set: ', len(train_index))

print('Verifying distribution ...')
train_table = df_train.rename(index=str, columns={'label':'training_count'})
test_table = df_test.rename(index=str, columns={'label':'test_count'})
verify = pd.concat([train_table.ix[:,len(df.columns)-2:].groupby('training_count').count(),
                    test_table.ix[:, len(df.columns)-2:].groupby('test_count').count()],axis = 1)

features_train = df_train.ix[:,:-2]
label_train = df_train.ix[:,-2]

print('Fitting model to predict question statements ...')
clf = RandomForestClassifier()
clf.fit(features_train, label_train)

predicted_label_train = clf.predict(features_train)

features_test = df_test.ix[:,:-2]
label_test = df_test.ix[:,-2]

print('Predicting question statement labels ... ')
predicted_label_test = clf.predict(features_test)

precision_train = precision_score(label_train, predicted_label_train, average='weighted')
recall_train = recall_score(label_train, predicted_label_train, average='weighted')
accuracy_train = accuracy_score(label_train, predicted_label_train)

precision_test = precision_score(label_test, predicted_label_test, average='weighted')
recall_test = recall_score(label_test, predicted_label_test, average='weighted')
accuracy_test = accuracy_score(label_test, predicted_label_test)

print('Training scores -----------------------------------')
print(classification_report(label_train, predicted_label_train))
print('accuracy score: ', accuracy_train)
print('Test scores ---------------------------------------')
print(classification_report(label_test, predicted_label_test))
print('accuracy score: ', accuracy_test)


# save model to disk
joblib.dump(clf, '../jiak_models/question_model.pkl', compress=9)
predicted_label_df = pd.Series(predicted_label_test, name="predicted")
predicted_label_df = predicted_label_df.reset_index(drop=True)
df_test = df_test.reset_index(drop=True)

import csv

output = pd.concat([df_test, predicted_label_df], axis=1)

output = output.iloc[:,[-3,-1,-2]]
output.to_csv('output.csv', quoting=csv.QUOTE_ALL,sep='|')

