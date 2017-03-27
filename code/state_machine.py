import nltk, sqlite3, re

class StateMachine:

    state = {
        'retrievable': False, # indicates whether there is enough info to retrieve
        'cuisines' : [],
        'foods' : [],
        'location' :[],
        'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'current_state': [0,0,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated
    }

    # Establish connection to SQL Database
    db_path = '../database/jiakbot.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Retrieve cuisine corpus as gazetteer / dictionary
    c.execute("SELECT DISTINCT LOWER(cuisine) FROM Cuisines")
    cuisines_dict = c.fetchall()
    cuisines_dict = [i[0] for i in cuisines_dict]

    # Retrieve food corpus as gazetteer / dictionary
    c.execute("SELECT DISTINCT LOWER(food) FROM foods")
    foods_dict = c.fetchall()
    foods_dict = [i[0] for i in foods_dict]

    def update_state(self, parsed_dict):

        updated = False

        tagged = nltk.pos_tag(nltk.word_tokenize(parsed_dict['input_text']))

        grammar = r"""
            FP: 
                {<VB.*><JJ.*|IN|>?<RB>?<NN.*>+}
                {<DT><JJ.*>?<NN.*>+}
                {<CC><JJ.*>?<NN.*>+}
            LP: 
                {<IN|TO><NN.*>+<VB.*|RB>?}
                {<IN|TO><JJ.*>?<NN.*>+?}
        """
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged)

        # Stop word removal
        stopword = ['good', 'nice', 'food', 'cuisine', 'restaurant', 'stall', 'place', 'today', 'morning', 'afternoon']

        # Identify cuisines and/or food items from user input
        foods_user = []
        for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
            leaves = subtree.leaves()
            for leaf in leaves:
                food = [w for (w, t) in leaves if re.search(r"(JJ.*|RB|NN.*)", t) and w not in stopword]
                food = ' '.join(food)
            foods_user.append(food)

        # Identify place / location from user input
        location_user = []
        for subtree in result.subtrees(filter=lambda t: t.label() == 'LP'):
            leaves = subtree.leaves()
            for leaf in leaves:
                location = [w for (w, t) in leaves if re.search(r"(JJ.*|NN.*|VB.*|RB)", t)]
                location = ' '.join(location)
            location_user.append(location)

        # Match user input on cuisines and/or food items against the cuisine corpus
        self.state['cuisines'] = [cuisine for cuisine in foods_user if cuisine in self.cuisines_dict]
        self.state['foods'] = [food for food in foods_user if food not in self.state['cuisines']]
        self.state['location'] = location_user

        # Udpate state
        self.state['previous_state'] = self.state['current_state']

        if len(self.state['cuisines']) > 0:
            self.state['current_state'][0] = 1

        if len(self.state['foods']) > 0:
            self.state['current_state'][1] = 1

        if len(self.state['location']) > 0:
            self.state['current_state'][2] = 1

        if self.state['previous_state'] == self.state['current_state']:
            updated = False
        else:
            updated = True

        return updated # returns True is updated
