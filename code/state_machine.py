import nltk, re
from collections import OrderedDict

class StateMachine:

    state = {
        'retrievable': False,  # indicates whether there is enough info to retrieve
        'cuisines': [],
        'foods': [],
        'locations': [],
        'previous_state': [0, 0, 0],  # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'current_state': [0, 0, 0],  # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'retrieved': False,
        'post_feedback': False,
        'recommendations': [],
        'session': OrderedDict()
    }

    # read in locations
    location_file = open('../corpus/knowledge/locations.txt','r')
    known_locations = [location.lower() for location in location_file.read().splitlines()]
    location_file.close()

    # read in cuisines
    cuisine_file = open('../corpus/knowledge/cuisines.txt', 'r')
    known_cuisines = [cuisine.lower() for cuisine in cuisine_file.read().splitlines()]
    cuisine_file.close()

    # read in food
    food_file = open('../corpus/knowledge/foods.txt', 'r')
    known_foods = [food.lower() for food in food_file.read().splitlines()]
    food_file.close()

    # custom non food words
    non_food_file = open('../corpus/knowledge/non_foods.txt', 'r')
    non_food_words = [non_food.lower() for non_food in non_food_file.read().splitlines()]
    non_food_file.close()

    def update_state(self, parsed_dict):

        self.state['retrievable'] = False
        updated = False

        tagged = nltk.pos_tag(nltk.word_tokenize(parsed_dict['input_text']))

        # define the grammar. FP = Food Phrase. LP = Location Phrase
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

        # ----------------------------------------------------------------------------
        # Identify cuisines and/or food items from user input
        # food and cuisine identified together and then separated
        # ----------------------------------------------------------------------------
        identified_food_cuisines = []

        for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
            leaves = subtree.leaves()
            food_cuisines = [w for (w, t) in leaves if re.search(r"(JJ.*|VB|RB|NN.*)", t) and w not in self.non_food_words]
            food_cuisines = ' '.join(food_cuisines)
            identified_food_cuisines.append(food_cuisines)



        # ----------------------------------------------------------------------------
        # identifying location
        # ----------------------------------------------------------------------------

        identified_locations = []

        for subtree in result.subtrees(filter=lambda t: t.label() == 'LP'):
            leaves = subtree.leaves()
            locations = [w for (w, t) in leaves if re.search(r"(JJ.*|NN.*|VB.*|RB)", t)]
            locations = ' '.join(locations)
            identified_locations.append(locations)



        # ----------------------------------------------------------------------------
        # for detected locations, check if its actually a food
        # ----------------------------------------------------------------------------

        not_location = [location.lower() for location in identified_locations if location.lower() not in self.known_locations]

        if len(not_location) > 0:
            retag = nltk.pos_tag(nltk.word_tokenize(', '.join(not_location)))

            f_grammar = r"""
                FP:
                    {<JJ>?<NN>+}
            """

            fcp = nltk.RegexpParser(f_grammar)
            result = fcp.parse(retag)

            for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
                leaves = subtree.leaves()
                food_cuisines = [w for (w, t) in leaves if re.search(r"(JJ.*|VB|RB|NN.*)", t) and w not in self.non_food_words]
                food_cuisines = ' '.join(food_cuisines)
                identified_food_cuisines.append(food_cuisines)

        # ----------------------------------------------------------------------------
        # finalize the identified lists
        # ----------------------------------------------------------------------------

        identified_foods = [phrase for phrase in identified_food_cuisines if phrase.lower() not in self.known_cuisines]
        identified_cuisines = [phrase for phrase in identified_food_cuisines if phrase.lower() in self.known_cuisines]
        identified_locations = [phrase for phrase in identified_locations if phrase.lower() not in not_location]
        #
        # print(identified_foods)
        # print(identified_cuisines)
        # print(identified_locations)

        # append to the state
        self.state['foods'].extend(identified_foods)
        self.state['cuisines'].extend(identified_cuisines)
        self.state['locations'].extend(identified_locations)

        # ----------------------------------------------------------------------------
        # all the logic to update the states
        # ----------------------------------------------------------------------------

        # Update state
        self.state['previous_state'] = self.state['current_state']

        if len(self.state['cuisines']) > 0:
            self.state['current_state'][0] = 1
            self.state['retrievable'] = True

        if len(self.state['foods']) > 0:
            self.state['current_state'][1] = 1
            self.state['retrievable'] = True

        if len(self.state['locations']) > 0:
            self.state['current_state'][2] = 1
            self.state['retrievable'] = True

        if self.state['previous_state'] == self.state['current_state']:
            updated = False
        else:
            updated = True

        return updated # returns True is updated

########################################################
# for testing purposes
########################################################
#
# sm = StateMachine()
#
# parsed_dict = {'nouns': ['raffles', 'place'],
#                'input_text': 'Recommend an japanese food place at Bras Basah',
#                'input_type': 'question',
#                'pronouns': ['what'],
#                'verbs': ['is'],
#                'cleansed_text': ['nice', 'raffles', 'place'],
#                'tokens': ['what', 'is', 'nice', 'at', 'raffles', 'place', '?'], 'adjs': ['nice'], 'adverbs': []}
#
# sm.update_state(parsed_dict=parsed_dict)
