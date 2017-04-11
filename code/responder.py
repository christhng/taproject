import configparser
import json
import random
from retriever import Retriever
from state_machine import StateMachine

# Set up
# ------------------------------------------------------------------------------
config_file_path = '../config_app/app_config.ini'

# Read in the config in the auth files
config = configparser.ConfigParser()
config.read(config_file_path)

# read in vocabularies
about_user_path = config['file_path']['about_user']
about_bot_path = config['file_path']['about_bot']
yes_or_no_path = config['file_path']['yes_or_no']

# read in the corpus paths
greeting_path = config['file_path']['greeting_corpus']
about_bot_responses_path = config['file_path']['about_bot_responses']
about_user_responses_path = config['file_path']['about_user_responses']
generic_resp_path = config['file_path']['generic_response_corpus']
yes_response_path = config['file_path']['yes_response_corpus']
question_to_feedback_path = config['file_path']['question_to_feedback_corpus']
response_to_rhetoric_path = config['file_path']['rhetoric_response_corpus']
further_probe_path = config['file_path']['further_probe_corpus']

# load data
greeting_data = json.load(open(greeting_path))
bot_references_data = json.load(open(about_bot_path))
about_bot_response_data = json.load(open(about_bot_responses_path))
user_references_data = json.load(open(about_user_path))
about_user_response_data = json.load(open(about_user_responses_path))
generic_corpus_data = json.load(open(generic_resp_path))
yes_or_no_data = json.load(open(yes_or_no_path))
yes_response_data = json.load(open(yes_response_path))
question_to_feedback_data = json.load(open(question_to_feedback_path))
response_to_rhetoric_data = json.load(open(response_to_rhetoric_path))
further_probe_data = json.load(open(further_probe_path))

# convert greeting data to dict
greetings = {
    "greetings": {}
}

for g in greeting_data['greetings']:
    greetings["greetings"][g[0].lower()] = g[1]

# Responder
# ------------------------------------------------------------------------------
class Responder:
    """
    Reponse constructor class

    Steps taken to create a response:
        1) Check if results are retrievable
        2a) If retrievable, Retrieve results from Retriever object
            2a-1) Check that there is content retrieved in results dictionary
            2a-2) Return response accordingly
                2a-2-a) If something is found - seek response (Was this useful?)
                    - Yes/No: reset state machine with proper response
                    - Anything else: AlternativeResponder
                2a-2-b) If nothing is found - reset state machine
        2b) If not retrievable, use AlternativeResponder object to generate
        response based on topic
    """

    greeting_corpus = greetings['greetings']
    bot_references = bot_references_data['about_bot']
    user_references = user_references_data['about_user']
    # sort yes_or_no_data into respective dicts
    yes_words = yes_or_no_data['yes']
    yes_response = yes_response_data['yes_response']
    # responses to questions user asks when bot asks for feedback
    question_to_feedback = question_to_feedback_data['question']
    # rhetoric responses
    rhetoric_responses = response_to_rhetoric_data['rhetoric_response']
    # words that encourage further probing
    further_probe_words = further_probe_data['probe_words']

    def get_response(self, state, parsed_dict):
        """
        Response controller

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed_dict (dict) - Dictionary passed from Parser object
        """

        # retrieve the input type - question, rhetoric, statement
        input_type = parsed_dict['input_type']
        valid_locations = ['city hall', 'raffles place', 'bras basah', 'dhoby ghaut']

        # logic to construct a sensible response
        # get topic from parsed_dict - greeting, bot, user
        # default response to be overriden
        topic = self._get_topic(parsed_dict)
        default_response = AlternativeResponder(parsed_topic=topic,
                                        parsed_dict=parsed_dict,
                                        input_type=input_type).construct()

        # is the user's input rhetorical?
        response = self._construct_response_to_rhetoric() if input_type == 'rhetoric' else default_response

        # if not let's continue checking other conditions for the most appropriate response
        retriever = Retriever()

        # check if state only has location to conduct query, or if it has food/cuisine
        if self._only_location(state):
            response_dict = self._construct_response_from_db(state, parsed_dict, retriever, random=True)
            response = "Sorry, sir - Jiakbot is not that well travelled." if state['locations'][0] not in valid_locations else response_dict['response']
            state['retrieved'] = False if state['locations'][0] not in valid_locations else response_dict['retrieved']
        elif self._food_and_or_cuisine(state):
            response_dict = self._construct_response(input_type, state, parsed_dict, retriever)
            response, state['retrieved'] = response_dict['response'], response_dict['retrieved']

        # reset query terms if items have been retrieved
        if state['retrieved']:
            state = self._reset_state(state)

        return response

    def _reset_state(self, state):
        state['cuisines'] = []
        state['foods'] = []
        state['locations'] = []
        return state

    def _construct_response_to_rhetoric(self):
        return random.choice(rhetoric_responses)

    def _only_location(self, state):
        if len(state['locations']) > 0 and len(state['foods']) == 0 and len(state['cuisines']) == 0:
            return True
        return False

    def _food_and_or_cuisine(self, state):
        if len(state['foods']) > 0 or len(state['cuisines']) > 0:
            return True
        elif state['retrieved']:
            return True
        return False

    def _construct_response(self, input_type, state, parsed_dict, retriever):
        response_dict = self._construct_response_from_db(state, parsed_dict, retriever) if state['retrievable'] else ''
        if not response_dict:
            response_dict = self._construct_response_to_feedback(parsed_dict, input_type, state, retriever) if state['retrieved'] else ''
        return response_dict


    def _construct_response_from_db(self, state, parsed_dict, retriever, random=False):
        """
        Response generated from a result that was successfully
        retrieved using Retriever

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed_dict (dict) - Dictionary passed from Parser object
        """

        result = retriever.get_random_business(parsed_dict)
        if not random:
            result = self._get_result_from_db(state, parsed_dict, retriever)

        # check if any results are returned
        try:
            if not result['biz_name']:
                # get similar business
                result = retriever.get_similar_business(state['foods'][0])
                response = self._get_similar_business(state, result)
                state = self._reset_state(state)
                retrieved = False
            else:
                response = "You can try {0}, it is rated {3} on our database. " \
                           "They serve {1}. \n" \
                           "One of our reviewers commented: \"{2}\". \n" \
                           "Is this what you are looking for?".format(result['biz_name'],
                                                                      result['category'],
                                                                      result['statement'],
                                                                      result['rating'])
                retrieved = True
        except TypeError: # if result is empty
            # get similar business
            result = retriever.get_similar_business(state['foods'][0])
            response = self._get_similar_business(state, result)
            state = self._reset_state(state)
            retrieved = False
        # prepare response
        return {'response': response, 'retrieved': retrieved}

    def _get_similar_business(self, state, result):
        response = 'Sorry, I wasn\'t able to find anything relevant to {0}! Maybe you can consider one of the following options?\n{1}'.format(state['foods'][0], ', '.join(result))
        return response

    def _construct_response_to_feedback(self, parsed_dict, input_type, state, retriever):
        """
        Response generated in response to feedback given to a
        prior recommendation.

        Arguments:
            parsed_dict (dict) - Dictionary passed from Parser object
        """
        # If bot asked for feedback and user, in turn, asked a question back
        retrieved = True
        # default response
        response = "Wah I don't understand sia, can just let me know whether my recommendation useful or not?"
        # check for intent
        further_probe = self._check_post_feedback_intent(parsed_dict)
        if further_probe:
            if retriever.retrieved_biz_type[-1] == 'food':
                result = retriever.get_business_by_food(parsed_dict,state)
            elif retriever.retrieved_biz_type[-1] == 'cuisine':
                result = retriever.get_business_by_cuisine(parsed_dict,state)
            elif retriever.retrieved_biz_type[-1] == 'food_cuisine':
                result = retriever.get_business_by_food_cuisine(parsed_dict, state)
            if result['biz_name']:
                response = "Ok, maybe you can try {0} instead! " \
                           "They serve {1}. \n" \
                           "Here's a statement someone made for {2}:\n{3} \n" \
                           "Here's a full review, " \
                           "if you bothered to read: \n{4}\n" \
                           "Is this what you are looking for?".format(result['biz_name'],
                                                                      result['category'],
                                                                      result['biz_name'],
                                                                      result['statement'],
                                                                      result['rating'])
            else:
                # no other suggestions
                response = "Sorry I can't find anything else liao!"
                retrieved = False
        elif input_type == 'question':
            response = random.choice(self.question_to_feedback)
        # If user gave a response that could be understood as 'yes' or 'no'
        else:
            for w in parsed_dict['tokens']:
                if w in self.yes_words:
                    response = random.choice(self.yes_response)
                    retrieved = False
        return {'response': response, 'retrieved': retrieved}


    def _get_result_from_db(self, state, parsed_dict, retriever):
        query_type = self._get_db_query_type(state)
        if not query_type:
            result = retriever.get_random_business(parsed_dict)
        elif query_type == 'foods':
            result = retriever.get_business_by_food(parsed_dict, state)
        elif query_type == 'cuisines':
            result = retriever.get_business_by_cuisine(parsed_dict, state)
        elif query_type == 'food_cuisine':
            result = retriever.get_business_by_food_cuisine(parsed_dict, state)
        return result

    def _get_db_query_type(self, state):
        if len(state['foods']) > 0 and not len(state['cuisines']) > 0:
            return 'foods'
        elif not len(state['foods']) > 0 and len(state['cuisines']) > 0:
            return 'cuisines'
        elif len(state['foods']) > 0 and len(state['cuisines']) > 0:
            return 'food_cuisine'
        else:
            return None

    def _check_post_feedback_intent(self, parsed_dict):
        for w in parsed_dict['tokens']:
            if w in self.further_probe_words:
                return True
        return False

    def _get_topic(self, parsed_dict):

        """
        Retrieve topic in order of importance.
        Order of importance:
            1) greeting
            2) bot reference
            3) user reference
        """

        for key in self.greeting_corpus.keys():
            if key in parsed_dict['tokens']:
                return 'greetings'

        for bot_ref in self.bot_references:
            if (bot_ref in parsed_dict['pronouns'] or bot_ref in parsed_dict['nouns']):
                return 'bot'

        for user_ref in self.user_references:
            if user_ref in parsed_dict['pronouns']:
                return 'user'

        return 'generic'

class AlternativeResponder:
    """
    Alternative response class

    Attributes:
        parsed_topic - A string representing the alternative topic of interest
        based on the parsed sentence
        topics - List of available topics
    """
    topics = ['bot', 'user', 'greetings', 'generic']
    responses = {
        **greetings, **about_bot_response_data,
        **about_user_response_data, **generic_corpus_data
    }

    def __init__(self, parsed_dict, parsed_topic, input_type):
        """
        Return AlternativeResponder object which will respond to
        a particular topic

        Available topics:
            bot - about the bot itself
            user - about the user
            greeting - general greetings
            vague - don't understand
        """

        self.parsed_dict = parsed_dict
        self.parsed_topic = parsed_topic
        self.input_type = input_type

    def _check_topic(self):
        """
        Checks if parsed_topic argument is in list of available topics
        """

        if self.parsed_topic in self.topics:
            return True
        return False

    def construct(self):
        """
        Constructs alternative response

        Arguments:
            parsed_topic (string) - string which represents a topic that the
            bot can comprehend
        """

        if self._check_topic():
            if self.parsed_topic == 'greetings':
                greetings = self.responses['greetings']
                for key in greetings.keys():
                    if key in self.parsed_dict['tokens']:
                        response = random.choice(greetings[key])

            else:
                response = random.choice(self.responses[self.parsed_topic])
        else:
            response = "Pardon?"
        return response
