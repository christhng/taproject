# import your libraries here
import sqlite3
import random
import nltk
import re
from nltk.tokenize import word_tokenize
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities

stop_list = nltk.corpus.stopwords.words('english')

class Retriever:

    db_path = '../database/jiakbot.db'

    def get_result(self,state,parsed_dict,previous_recommendation=[],anything=False):

        result = {
            'biz_id':'',
            'biz_name':'',
            'biz_location':'',
            'category':'',
            'review':'',
            'statement':'',
            'rating':'',
            'has_result':False
        }

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # select most recent food input from the state object
        food = None
        if len(state['foods']) > 0:
            food = state['foods'][0]

        # select most recent cuisine input from the state object
        cuisine = None
        if len(state['cuisines']) > 0:
            cuisine = state['cuisines'][0]
        existing_recommendations = ""
        if previous_recommendation:
            existing_recommendations = " AND b.biz_name NOT IN (" + ",".join('"' + rec + '"' for rec in previous_recommendation) + ") "
            foods = [session['foods'][0] if len(session['foods']) > 0 else '' for session in state['session'].values()]
            cuisines = [session['cuisines'][0] if len(session['cuisines']) > 0 else '' for session in state['session'].values()]
            if len(foods) > 0:
                foods.reverse()
                try:
                    food = next(f for f in foods if f)
                except StopIteration:
                    pass
            if len(cuisines) > 0:
                cuisines.reverse()
                try:
                    cuisine = next(c for c in cuisines if c)
                except StopIteration:
                    pass

        if existing_recommendations and food:
            # based on state (which contains food, cuisine, location) get 1 business that matches
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "WHERE lower(f.food) LIKE '%{0}%'".format(food) + existing_recommendations + \
                      "ORDER BY b.biz_rating DESC LIMIT 10;"
        elif existing_recommendations and cuisine:
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                      "WHERE lower(c.cuisine) LIKE '%{0}%'".format(cuisine) + existing_recommendations + \
                      "ORDER BY b.biz_rating DESC LIMIT 10;"
        elif existing_recommendations and food and cuisine:
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                      "WHERE lower(c.cuisine) LIKE '%{0}%' OR lower(f.food) LIKE '%{1}%' ".format(food, cuisine) + existing_recommendations + \
                      "ORDER BY b.biz_rating DESC LIMIT 10;"
        elif food and not cuisine:
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "WHERE lower(f.food) LIKE '%{0}%' " \
                      "ORDER BY b.biz_rating DESC LIMIT 10;".format(food)
        elif not food and cuisine:
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                      "WHERE lower(c.cuisine) LIKE '%{0}%' " \
                      "ORDER BY b.biz_rating DESC LIMIT 10;".format(cuisine)
        elif food and cuisine:
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                      "WHERE lower(c.cuisine) LIKE '%{0}%' OR lower(f.food) LIKE '%{1}%' " \
                      "ORDER BY b.biz_rating DESC LIMIT 10;".format(food, cuisine)

        if anything:
            # override everything and pick any random food place
            sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                      "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                      "ORDER BY b.biz_rating DESC LIMIT 10;"

        # get the business details for the food
        c.execute(sql_str)
        businesses = c.fetchall()

        if len(businesses) == 0:
            c.close()
            return result

        # randomly select a result based on results
        selected_biz = businesses[random.randint(0,len(businesses))]

        biz_id = selected_biz[0]
        result['biz_id'] = selected_biz[0]  # 0 corresponds to column 1 which is the biz_id
        result['biz_name'] = selected_biz[1] # 1 corresponds to column 2 of the result which is biz_name
        result['category'] = selected_biz[2] # 2 corresponds to column 3.. the type of food they serve

        # --------------------------------------------------------------------
        # based on jaccard, levenshtein or cosine similarity get 1 comment
        # added code based on cosine similarity to retrieve list of reviews based on biz_id

        # Step 1: Fetch all the statements based on biz_id
        # --------------------------------------------------------------------------
        sql_str = "SELECT r.biz_id, r.description, s.stmt FROM reviews r " \
                  "LEFT JOIN stmts s ON r.review_id = s.review_id " \
                  "WHERE r.biz_id = '{0}';".format(biz_id)
        #
        # c.execute(sql_str)
        # results = c.fetchall()

        results = []
        tokenized_docs = []
        processed_docs = []

        for row in c.execute(sql_str):
            doc = word_tokenize(row[2])
            tokenized_docs.append(doc)
            results.append(row)

        processed_docs = [[w.lower() for w in doc] for doc in tokenized_docs]
        processed_docs = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in processed_docs]
        processed_docs = [[w for w in doc if w not in stop_list] for doc in processed_docs]

        # Step 2: Select most similar review based on query using cosine similarity
        # --------------------------------------------------------------------------

        reviews = corpora.Dictionary(processed_docs)

        r_vecs = [reviews.doc2bow(doc) for doc in processed_docs]
        r_tfidf = models.TfidfModel(r_vecs)
        r_vecs_with_tfidf = [r_tfidf[vec] for vec in r_vecs]

        r_index = similarities.SparseMatrixSimilarity(r_vecs_with_tfidf, len(reviews))

        query = parsed_dict['tokens']
        query_vec = reviews.doc2bow(query)
        query_vec_tfidf = r_tfidf[query_vec]

        q_sims = r_index[query_vec_tfidf]
        q_sorted_sims = sorted(enumerate(q_sims), key=lambda item: -item[1])

        # print( q_sorted_sims )

        # Step 3: Return most relevant review back
        # --------------------------------------------------------------------------

        most_similar_stmt_id = q_sorted_sims[0][0]
        result['review'] = results[most_similar_stmt_id][1]
        result['statement'] = results[most_similar_stmt_id][2]

        c.close()

        return result
