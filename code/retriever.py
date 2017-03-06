# import your libraries here
import sqlite3
import random

class Retriever:

    db_path = '../database/jiakbot.db'

    def get_result(self,state,parsed):

        result = {
            'biz_name':'',
            'biz_location':'',
            'category':'',
            'comment':''
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
        # print(selected_biz)

        result['biz_name'] = selected_biz[1] # 2 corresponds to column 2 of the result which is biz_name
        biz_id = selected_biz[0] # 1 corresponds to column 1 which is the biz_id

        # --------------------------------------------------------------------
        # based on jaccard, levenshtein or cosine similarity get 1 comment
        # print("hello|world".split(sep="|"))
        result['comment'] = 'food is awful...' # return the result

        return result

r = Retriever()

parsed_dict = {
            'tokens': ['japanese','ramen'],
            'input_text': 'i like to eat japanese ramen',  # string
            'cleansed_text': 'eat japanese ramen',  # string
            'verbs': ['eat'],
            'adverbs': [],
            'nouns': ['japanese','ramen'],
            'adjs': [],
            'pronouns': [],
            'is_question':False
        }

state = {
        'retrievable': False, # indicates whether there is enough info to retrieve
        'cuisines' : ['japanese'],
        'foods' : ['ramen','sushi','teppan yaki'],
        'location' :[],
        'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'current_state': [1,1,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated
    }



# print(r.get_result(state,parsed_dict))