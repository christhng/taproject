import configparser
import json
import random
from retriever import Retriever

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
no_response_path = config['file_path']['no_response_corpus']

# load data
greeting_data = json.load(open(greeting_path))
bot_references_data = json.load(open(about_bot_path))
about_bot_response_data = json.load(open(about_bot_responses_path))
user_references_data = json.load(open(about_user_path))
about_user_response_data = json.load(open(about_user_responses_path))
generic_corpus_data = json.load(open(generic_resp_path))
yes_or_no_data = json.load(open(yes_or_no_path))
yes_response_data = json.load(open(yes_response_path))
no_response_data = json.load(open(no_response_path))

# convert greeting data to dict
greetings = {
    "greetings": {}
}

for g in greeting_data['greetings']:
    greetings["greetings"][g[0].lower()] = g[1]


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
    no_words = yes_or_no_data['no']
    yes_response = yes_response_data['yes_response']
    no_response = no_response_data['no_response']

    def get_response(self, state, parsed_dict):
        """
        Response controller

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed (dict) - Dictionary passed from Parser object
        """

        # if retrievable go retrieve the biz name, location and 1 line of review
        if state['retrievable']:
            response_dict = self._contruct_response_from_db(state, parsed_dict)
            response = response_dict['response']
            retrieved = response_dict['retrieved']
            state['retrieved'] = retrieved
        # detect if previous statement was a recommendation
        elif state['retrieved']:
            response = self._construct_response_to_feedback(parsed_dict)
            state['retrieved'] = False # reset retrieved status
        # logic to construct a sensible response
        else:
            topic = self._get_topic(parsed_dict)
            response = AlternativeResponder(
                parsed_topic=topic,
                parsed_dict=parsed_dict
                ).construct()
        return response

    def _contruct_response_from_db(self, state, parsed_dict):
        """
        Response generated from a result that was successfully
        retrieved using Retriever

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed_dict (dict) - Dictionary passed from Parser object
        """

        retriever = Retriever()
        result = retriever.get_result(state, parsed_dict)

        # check if any results are returned
        if not result['biz_name']:
            response = 'Sorry, I wasn\'t able to find anything relevant! Try something else.'
            retrieved = False
        else:
            response = "You can try {0}. " \
                       "They serve {1}. " \
                       "Here's a statement someone made for {2}:\n{3} \n" \
                       "Here's a full review, " \
                       "if you bothered to read: \n{4}\n" \
                       "Is this what you are looking for?".format(result['biz_name'],
                                                                  result['category'],
                                                                  result['biz_name'],
                                                                  result['statement'],
                                                                  result['review'])
            retrieved = True
        # prepare response
        return {'response': response, 'retrieved': retrieved}

    def _construct_response_to_feedback(self, parsed_dict):
        """
        Response generated in response to feedback given to a
        prior recommendation.

        Arguments:
            parsed_dict (dict) - Dictionary passed from Parser object
        """
        for w in parsed_dict['tokens']:
            if w in self.yes_words:
                response = random.choice(self.yes_response)
            elif w in self.no_words:
                response = random.choice(self.no_response)
        return response

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

    def __init__(self, parsed_dict, parsed_topic):
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

    def check_topic(self):
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

        if self.check_topic():
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
