# import relevant stuff here

class StateMachine:

    state = {
        'retrievable': False, # indicates whether there is enough info to retrieve
        'cuisines' : [],
        'foods' : [],
        'location' :[],
        'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
        'current_state': [0,0,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated
    }

    def update_state(self, parsed_dict):

        updated = False

        # check for cuisines using _check_cuisine function
        # check for food using _check_food function
        # check for location using _check_location function

        # updates the state variable state

        return updated # returns True is updated

    # think of a way to retrieve cuisines, food and location from tokens
    # probably by looking up a list

    def _check_cuisine(self,tokens):

        cuisine = []

        return cuisine # return the cuisines found

    def _check_food(self,tokens):

        food = []

        return food # return the food found

    def _check_location(self,tokens):

        location = []

        return location # return the location found