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

    _db_path = '../database/jiakbot.db'

    retrieved_biz_id = []
    retrieved_biz_type = [] # keeps track of whether the biz_id was found via food or cuisine

    def get_business_by_food(self,parsed_dict,state): # guaranteed to be different each time

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'statement': '',
            'rating': ''
        }

        # set requested food for retrieval
        requested_food = state['foods'][len(state['foods'])-1] if len(state['foods']) > 0 else ''

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "WHERE lower(f.food) LIKE '%{0}%'".format(requested_food) + " " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  #  biz_id
        business['biz_name'] = result[1] #  biz_name
        business['category'] = result[2] #  the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt(parsed_dict,biz_id)

        self.retrieved_biz_id.extend([biz_id])
        self.retrieved_biz_type.extend(['food'])

        return business


    def get_business_by_cuisine(self,parsed_dict,state): # guaranteed to be different each time

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'statement': '',
            'rating': ''
        }

        # set requested food for retrieval
        requested_cuisine = state['cuisines'][len(state['cuisines']) - 1] if len(state['cuisines']) > 0 else ''

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                  "WHERE lower(c.cuisine) LIKE '%{0}%' ".format(requested_cuisine) + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 10;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  # biz_id
        business['biz_name'] = result[1]  # biz_name
        business['category'] = result[2]  # the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt(biz_id)

        self.retrieved_biz_id.extend([biz_id])
        self.retrieved_biz_type.extend(['cuisine'])

        return business

    def get_business_by_food_cuisine(self,parsed_dict,state): # guaranteed to be different each time

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'statement': '',
            'rating': ''
        }

        # set requested food for retrieval
        requested_food = state['foods'][len(state['foods'])-1] if len(state['foods']) > 0 else ''
        requested_cuisine = state['cuisines'][len(state['cuisines']) - 1] if len(state['cuisines']) > 0 else ''

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                  "WHERE lower(c.cuisine) LIKE '%{0}%' " \
                  "OR lower(f.food) LIKE '%{1}%' ".format(requested_food, requested_cuisine) + " " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  #  biz_id
        business['biz_name'] = result[1] #  biz_name
        business['category'] = result[2] #  the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt(parsed_dict,biz_id)

        self.retrieved_biz_id.extend([biz_id])
        self.retrieved_biz_type.extend(['food_cuisine'])

        return business

    def get_random_business(self,parsed_dict):

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id WHERE 1 = 1 " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  # biz_id
        business['biz_name'] = result[1]  # biz_name
        business['category'] = result[2]  # the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt(parsed_dict,biz_id)

        self.retrieved_biz_id.extend([biz_id])
        self.retrieved_biz_type.extend(['random'])

        return business

    def get_random_similar_stmt(self,parsed_dict,biz_id):

        statement = ''

        # Step 1: Select all statements
        sql_str = "SELECT r.biz_id, r.description, s.stmt FROM reviews r " \
                  "LEFT JOIN stmts s ON r.review_id = s.review_id " \
                  "WHERE r.biz_id = '{0}';".format(biz_id)


        results = []
        tokenized_docs = []

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for row in c.execute(sql_str):
            doc = word_tokenize(row[2])
            tokenized_docs.append(doc)
            results.append(row)

        conn.close()

        processed_docs = [[w.lower() for w in doc] for doc in tokenized_docs]
        processed_docs = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in processed_docs]
        processed_docs = [[w for w in doc if w not in stop_list] for doc in processed_docs]

        # Step 2: Select most similar review based on query using cosine similarity

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

        # Step 3: Return most relevant statement back
        most_similar_stmt_id = q_sorted_sims[0][0]
        statement = results[most_similar_stmt_id][2]

        return statement

    def _get_biz_id_exclude_str(self):
        str = ''

        if len(self.retrieved_biz_id) > 0:
            biz_ids_str = ",".join('"' + biz_id + '"' for biz_id in self.retrieved_biz_id)
            str = "AND b.biz_id NOT IN ("+ biz_ids_str + ")"

        return str

########################################################
# for testing purposes
########################################################

# r = Retriever()
# state = {'current_state': [1, 1, 0],
#          'retrievable': True,
#          'post_feedback': False,
#          'previous_state': [1, 1, 0],
#          'recommendations': [],
#          'cuisines': ['japanese'],
#          'locations': [],
#          'retrieved': False,
#          'foods': ['burgers']}
#
# parsed_dict = {'tokens': ['you', 'know', 'of', 'any', 'place', 'for', 'japanese', 'or', 'sells', 'burgers', '?']}
# print(r.get_business_by_food(parsed_dict=parsed_dict, state=state))
# print(r.get_business_by_food(parsed_dict=parsed_dict, state=state))
# print(r.get_business_by_food(parsed_dict=parsed_dict, state=state))
# print(r.get_business_by_food(parsed_dict=parsed_dict, state=state))
# print(r.get_business_by_cuisine(parsed_dict=parsed_dict, state=state))
# print(r.get_random_business())
#
# print(r.retrieved_biz_id)
