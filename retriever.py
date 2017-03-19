# import your libraries here
import sqlite3
import random
import nltk 
import re
from nltk.tokenize import word_tokenize
stop_list = nltk.corpus.stopwords.words('english')

class Retriever:

    db_path = '../database/jiakbot.db'

    def get_result(self,state,parsed):

        result = {
            'biz_name':'',
            'biz_location':'',
            'category':'',
            'comment':'',
            'rating':''
        }

        # connect and write to database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # randomly select food (ignore for now)
        # food = state['foods'][random.randint(0,len(state['foods']))]

        # select most recent food input from the state object
        food = state['foods'][0]

        # select most recent cuisine input from the state object
        cuisine = state['cuisines'][0]

        # based on state (which contains food, cuisine, location) get 1 business that matches
        sql_str = "SELECT * FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "WHERE lower(f.food) = '%s' " \
                  "ORDER BY b.biz_rating DESC;" % food

        # get the business details for the food
        c.execute(sql_str)
        businesses = c.fetchall()

        # randomly select a result based on results
        selected_biz = businesses[random.randint(0,len(businesses))]
        print(selected_biz)

        result['biz_name'] = selected_biz[1] # 2 corresponds to column 2 of the result which is biz_name
        biz_id = selected_biz[0] # 1 corresponds to column 1 which is the biz_id

        # --------------------------------------------------------------------
        # based on jaccard, levenshtein or cosine similarity get 1 comment
        # added code based on cosine similarity to retrieve list of reviews based on biz_id
        t = (biz_id,)
                
        '''
        Step 1: Fetech all the reviews based on biz_id
        '''
        
        c.execute("SELECT description FROM reviews WHERE biz_id=?",t)
        results = c.fetchall()
        
                
        docs1=[]
        for i in results:
            doc = word_tokenize(i[0])
            docs1.append(doc)
            docs2 = [[w.lower() for w in doc] for doc in docs1]
            docs3 = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in docs2]
            docs4 = [[w for w in doc if w not in stop_list] for doc in docs3]


        '''
        Step 2: Select most similar review based on query using cosine similarity
        '''
        
        import gensim
        from gensim import corpora
        reviews = corpora.Dictionary(docs4)
        print(reviews)
                    
        import gensim
        from gensim import models
        r_vecs = [reviews.doc2bow(doc) for doc in docs4]
        r_tfidf = models.TfidfModel(r_vecs)
        r_vecs_with_tfidf = [r_tfidf[vec] for vec in r_vecs]
        
        
        from gensim import similarities
        r_index = similarities.SparseMatrixSimilarity(r_vecs_with_tfidf, 96)
        
        print("\n")
        
        query = parsed_dict['tokens']
        query_vec = reviews.doc2bow(query)
        query_vec_tfidf = r_tfidf[query_vec]
        q_sims = r_index[query_vec_tfidf]
        q_sorted_sims = sorted(enumerate(q_sims), key=lambda item: -item[1])
        
        print(parsed_dict['tokens'])
        print("\n")
        print("The most similar document is number: " + str(q_sorted_sims[0][0]))
        print("\n")
        print("The similarity based on documents is based on the ranking:"+ str(q_sorted_sims[0:10]))

        '''
        Step 3: Return most relevant review back
        '''
        
        c.execute("SELECT review_id, description FROM reviews WHERE biz_id=?",t)
        returnremarks = c.fetchall()
        
        docschosen=[]
        for h in returnremarks:
            doc = word_tokenize(i[0])
            docschosen.append(doc)   
            docslower = [[w.lower() for w in doc] for doc in docschosen]
            docswords = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in docslower]
            final_docs= [[w for w in doc if w not in stop_list] for doc in docswords]
                    

        print("\n")
        print("The dictionary for the most related review is as below:")
        print(docschosen[(q_sorted_sims[0][0])])
        print("\n")
        print("\n")
        result['comment'] = results[0][(q_sorted_sims[0][0])]
        result['category'] = selected_biz[2]
        result['rating'] = selected_biz[3]
        

        return result


r = Retriever()

parsed_dict = {
            'tokens': ['like','eat','malay','nasi lemak'],
            'input_text': 'i like to eat malay nasi lemak',  # string
            'cleansed_text': 'eat nasi lemak',  # string
            'verbs': ['eat'],
            'adverbs': [],
            'nouns': ['malay','nasi lemak'],
            'adjs': [],
            'pronouns': [],
            'is_question':False
        }

state = {
        'retrievable': False, # indicates whether there is enough info to retrieve
        'cuisines' : ['malay'],
        'foods' : ['nasi lemak'],
        'location' :[],
        'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'current_state': [1,1,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated
    }



print(r.get_result(state,parsed_dict))