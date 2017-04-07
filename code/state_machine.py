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
                {<VB.*><JJ.*|IN>?<RB>?<NN.*>+}
                {<DT><JJ.*>?<NN.*>+}
                {<CC><JJ.*>?<NN.*>+}

            LP:
                {<IN|TO><NN.*>+<VB.*|RB>?}
                {<IN|TO><JJ.*>?<NN.*>+?}
                {<NN.*>+<VBP>+}
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
            food_cuisines = [w for (w, t) in leaves if re.search(r"(JJ.*|RB|NN.*)", t) and w not in self.non_food_words]
            food_cuisines = ' '.join(food_cuisines)
            if food_cuisines != '':
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
                food_cuisines = [w for (w,t) in leaves if re.search(r"(JJ|NN)", t) and w not in self.non_food_words]
                food_cuisines = ' '.join(food_cuisines)
                if food_cuisines != '':
                    identified_food_cuisines.extend([food_cuisines])

        # ----------------------------------------------------------------------------
        # finalize the identified lists
        # ----------------------------------------------------------------------------

        identified_foods = [phrase for phrase in identified_food_cuisines if phrase.lower() not in self.known_cuisines]
        identified_cuisines = [phrase for phrase in identified_food_cuisines if phrase.lower() in self.known_cuisines]
        identified_locations = [phrase for phrase in identified_locations if phrase.lower() not in not_location]

        # append to the state
        self.state['foods'].extend(identified_foods)
        self.state['cuisines'].extend(identified_cuisines)
        self.state['locations'].extend(identified_locations)

        # ----------------------------------------------------------------------------
        # all the logic to update the states
        # ----------------------------------------------------------------------------

        # Update state
        self.state['previous_state'] = self.state['current_state']
        input_num = 1

        if self.state['session'].keys():
            input_num = max(self.state['session'].keys()) + 1

        self.state['session'][input_num] = {
            'foods': self.state['foods'],
            'cuisines': self.state['cuisines'],
            'locations': self.state['locations']
        }

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

sm = StateMachine()

parsed_dict = {'input_text': 'hey'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want to have burgers or japanese food'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i get katong laksa around here?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'any good tonkatsu or yakitori place nearby?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where is a good place for french food'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'got any places serving fish & chips in shenton way'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'what food is good and cheap near simei'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'get me some hot and spicy chicken wings'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'any place serving good porterhouse steaks in marina bay?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'recommend an Australian barbecue restaurant'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i get authentic seafood paella in city hall'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'any place serving blue mountain coffee?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'Recommend a spanish tapas place near bugis'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i find cheap szechuan food'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want to eat salad today'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want a different food place, please recommend?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'when is the best time to go for lunch in CBD?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want to eat bak kut teh'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'my boss bringing us out for chilli crab or black pepper crab, quick recommend a place'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want hawker stalls selling western food'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i find fish head curry in little india'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want to have japanese monster curry rice today'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'I am going to Jurong East. Recommend a place for chinese food'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i get the best roti plata in kovan'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'lazy to think what to eat today. recommend anything'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'i want to have beef horfun today'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i get penang char koay teow around dhoby ghaut'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'let us go for pipa duck today'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'my friend suggest to go for chicken rice. where is the nearest place?'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))

parsed_dict = {'input_text': 'where can i get pork knuckles with beer the german way'}
sm.update_state(parsed_dict=parsed_dict)
print('original statement:', parsed_dict['input_text'])
print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.state['foods'],sm.state['cuisines'],sm.state['locations'],'\n'))
