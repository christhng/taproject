import nltk, sqlite3, re

class StateMachine:

    state = {
        'retrievable': False, # indicates whether there is enough info to retrieve
        'cuisines' : [],
        'foods' : [],
        'location' :[],
        'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'current_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'retrieved': False
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

    # location dictionary
    location_dict = ['Alexandra', 'Aljunied', 'Geylang', 'Ayer Rajah', 'Balestier', 'Bartley', 'Bishan',
                     'Marymount', 'Sin Ming', 'Bukit Timah', 'Buona Vista', 'Holland Village', 'one-north',
                     'Ghim Moh', 'Chinatown', 'Clarke Quay', 'City Hall', 'Kreta Ayer', 'Telok Ayer',
                     'Kallang', 'Bendemeer', 'Geylang Bahru', 'Kallang Bahru', 'Kallang Basin', 'Kolam Ayer',
                     'Tanjong Rhu', 'Mountbatten', 'Old Airport', 'Lavender', 'Boon Keng', 'Kent Ridge',
                     'Kim Seng', 'Little India', 'Farrer Park', 'Jalan Besar', 'MacPherson', 'Marina Bay',
                     'Esplanade', 'Marina Bay Sands', 'Marina Centre', 'Marina East', 'Marina South',
                     'Mount Faber', 'Mount Vernon', 'Museum', 'Newton', 'Novena', 'Orchard Road',
                     'Dhoby Ghaut', 'Emerald Hill', 'Tanglin', 'Outram', 'Pasir Panjang', 'Paya Lebar', 'Eunos',
                     'Geylang East', 'Potong Pasir', 'Rochor-Kampong Glam', 'Bencoolen', 'Bras Basah',
                     'Bugis', 'Queenstown', 'Dover', 'Commonwealth', 'Raffles Place', 'River Valley',
                     'Singapore River', 'Southern Islands', 'Tanjong Pagar', 'Shenton Way', 'Telok Blangah',
                     'Bukit Chandu', 'Bukit Purmei', 'HarbourFront', 'Keppel', 'Radin Mas', 'Mount Faber',
                     'Tiong Bahru', 'Bukit Ho Swee', 'Bukit Merah', 'Toa Payoh', 'Bukit Brown',
                     'Caldecott Hill', 'Thomson', 'Whampoa', 'St. Michael', 'Bedok', 'Bedok Reservoir',
                     'Chai Chee', 'Kaki Bukit', 'Tanah Merah', 'Changi', 'Changi Bay', 'Changi East',
                     'Changi Village', 'East Coast', 'Joo Chiat', 'Katong', 'Kembangan', 'Pasir Ris',
                     'Elias', 'Lorong Halus', 'Loyang', 'Marine Parade', 'Siglap', 'Tampines', 'Simei',
                     'Ubi', 'Central Catchment Nature Reserve', 'Kranji', 'Lentor', 'Lim Chu Kang',
                     'Neo Tiew', 'Sungei Gedong', 'Mandai', 'Sembawang', 'Canberra', 'Senoko', 'Simpang',
                     'Sungei Kadut', 'Woodlands', 'Admiralty', 'Innova', 'Marsiling', 'Woodgrove',
                     'Yishun', 'Chong Pang', 'Ang Mo Kio', 'Cheng San', 'Chong Boon', 'Kebun Baru',
                     'Teck Ghee', 'Yio Chu Kang', 'Bidadari', 'Hougang', 'Defu', 'Kovan', 'Lorong Chuan',
                     'North-Eastern Islands', 'Punggol', 'Punggol Point', 'Punggol New Town', 'Seletar',
                     'Sengkang', 'Serangoon', 'Serangoon Gardens', 'Serangoon North', 'Boon Lay', 'Tukang',
                     'Liu Fang', 'Samulun', 'Shipyard', 'Bukit Batok', 'Bukit Gombak', 'Hillview', 'Guilin',
                     'Bukit Batok West', 'Bukit Batok East', 'Bukit Panjang', 'Choa Chu Kang', 'Yew Tee',
                     'Clementi', 'Toh Tuck', 'West Coast', 'Pandan', 'Jurong East', 'Toh Guan',
                     'Teban Gardens', 'Penjuru', 'Yuhua', 'Jurong Regional Centre', 'Jurong Lake',
                     'Jurong River', 'Jurong Port', 'Jurong West', 'Hong Kah', 'Taman Jurong',
                     'Boon Lay Place', 'Chin Bee', 'Yunnan', 'Jurong Central', 'Kian Teck', 'Safti',
                     'Wenya', 'Lim Chu Kang', 'Pioneer', 'Joo Koon', 'Gul Circle', 'Pioneer Sector',
                     'Tengah', 'Tuas', 'Wrexham', 'Promenade', 'Pioneer', 'Soon Lee', 'Tuas South',
                     'Murai', 'Sarimbun']

    location_dict_lc = [w.lower() for w in location_dict]

    def update_state(self, parsed_dict):

        self.state['retrievable'] = False
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
                place = [w for (w, t) in leaves if re.search(r"(JJ.*|NN.*|VB.*|RB)", t)]
                place = ' '.join(place)
            location_user.append(place)

        not_location = [location.lower() for location in location_user if location.lower() not in self.location_dict_lc]

        # Additional checks for food items in user input
        if len(not_location) > 0:
            tagged1 = nltk.pos_tag(nltk.word_tokenize(', '.join(not_location)))

            fgrammar = r"""
                FP:
                    {<JJ>?<NN>+}
            """
            fcp = nltk.RegexpParser(fgrammar)
            result = fcp.parse(tagged1)

            for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
                leaves = subtree.leaves()
                for leaf in leaves:
                    food = [w for (w, t) in leaves if re.search(r"(JJ|NN)", t) and w not in stopword]
                    food = ' '.join(food)
                foods_user.append(food)

        # Match user input on cuisines and/or food items against the cuisine corpus
        self.state['cuisines'] = [cuisine for cuisine in foods_user if cuisine in self.cuisines_dict]
        self.state['foods'] = [food for food in foods_user if food not in self.state['cuisines']]
        self.state['location'] = location_user

        # Update state
        self.state['previous_state'] = self.state['current_state']

        if len(self.state['cuisines']) > 0:
            self.state['current_state'][0] = 1
            self.state['retrievable'] = True

        if len(self.state['foods']) > 0:
            self.state['current_state'][1] = 1
            self.state['retrievable'] = True

        if len(self.state['location']) > 0:
            self.state['current_state'][2] = 1
            self.state['retrievable'] = True

        if self.state['previous_state'] == self.state['current_state']:
            updated = False
        else:
            updated = True

        return updated # returns True is updated
