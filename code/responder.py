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

# read in the corpus paths
greeting_path = config['file_path']['greeting_corpus']
about_bot_responses_path = config['file_path']['about_bot_responses']
about_user_responses_path = config['file_path']['about_user_responses']
generic_resp_path = config['file_path']['generic_response_corpus']

# load data
greeting_data = json.load(open(greeting_path))
bot_references_data = json.load(open(about_bot_path))
about_bot_response_data = json.load(open(about_bot_responses_path))
user_references_data = json.load(open(about_user_path))
about_user_response_data = json.load(open(about_user_responses_path))
generic_corpus_data = json.load(open(generic_resp_path))

# convert greeting data to dict
greetings = {
    "greetings": {}
}
for g in greeting_data['greetings']:
    greetings["greetings"][g[0].lower()] = g[1]


class TopicRetriever:
    """
    Topic parser class

    Attributes:
        parsed_dict (dict) - dictionary of parsed words from Parser object
    """

    greeting_corpus = greetings['greetings']
    bot_references = bot_references_data['about_bot']
    user_references = user_references_data['about_user']

    def __init__(self, parsed_dict):
        self.parsed_dict = parsed_dict

    def retrieve(self):
        """
        Retrieve topic in order of importance.

        Order of importance:
            1) greeting
            2) bot reference
            3) user reference
        """

        assert isinstance(self.parsed_dict, dict)

        for key in self.greeting_corpus.keys():
            # print(key)
            if key in self.parsed_dict['tokens']:
                return 'greetings'

        for bot_ref in self.bot_references:
            if (bot_ref in self.parsed_dict['pronouns']
                or bot_ref in self.parsed_dict['nouns']):
                return 'bot'

        for user_ref in self.user_references:
            if user_ref in self.parsed_dict['pronouns']:
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


class Responder:
    """
    Reponse constructor class

    Steps taken to create a response:
        1) Check if results are retrievable
        2a) If retrievable, Retrieve results from Retriever object
            2a-1) Check that there is content retrieved in results dictionary
            2a-2) Return response accordingly
        2b) If not retrievable, use AlternativeResponder object to generate
        response based on topic
    """

    def check_retrieve(self, result):
        """
        Checks whether response dict is empty

        Arguments:
            result (dict) - results retrieved using Retriever object
        """

        for key in result.keys():
            if not result[key]:
                return False # If result[key] is empty
        return True

    def response_constructor(self, result):
        """
        Constructs response

        Arguments:
            result (dict) - results retrieved using Retriever object
        """

        # ensure dict is passed
        if isinstance(result, dict):
            # convert key-value pairs to variables
            for k, v in result.items():
                exec(k + '=' + v)
            # format response
            response = '''
            You can try %s at %s. They serve %s food. Here's
            a review someone had for %s:\n
            %s
            ''' % (biz_name, biz_location, category, biz_name, comment)
            return response
        else:
            msg = "Response constructor only accepts %s \
            argument. Instead, %s was used." % (str(type(dict())),
                                                str(type(result)))
            raise TypeError(msg)

    def retrievable_response(self, state, parsed):
        """
        Response generated from a result that was successfully
        retrieved using Retriever

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed (dict) - Dictionary passed from Parser object
        """

        retriever = Retriever()
        result = retriever.get_result(state, parsed)
        # check result is populated
        if self.check_retrieve(result):
            # construct positive response
            response = self.response_constructor(result)
        else:
            # construct negative response
            response = 'Sorry, I wasn\'t able to find anything relevant! :('
        # prepare response
        return response

    def prepare_response(self, state, parsed):
        """
        Response controller

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed (dict) - Dictionary passed from Parser object
        """

        # if retrievable go retrieve the biz name, location
        # and 1 line of review
        if state['retrievable'] is True:
            response = self.retrievable_response(state, parsed)
        else:
            topic = TopicRetriever(parsed_dict=parsed).retrieve()
            response = AlternativeResponder(
                parsed_topic=topic,
                parsed_dict=parsed
                ).construct()
        return response


# Uncomment to test
#
# non_retrievable_state = {
#     'retrievable': False, # indicates whether there is enough info to retrieve
#     'cuisines' : [],
#     'foods' : [],
#     'location' :[],
#     'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
#     'current_state': [0,0,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated
# }
# non_retrievable_parsed = {
#     'tokens': ['hello', ',', 'nice', 'to', 'meet', 'you'],
#     'input_text' : "Hello, nice to meet you", # string
#     'cleansed_text' : "hello nice meet you", # string
#     'verbs' :['meet'],
#     'adverbs': [],
#     'nouns': [] ,
#     'adjs': ['nice'],
#     'pronouns':['you']
# }
#
# retrievable_state = {
#     'retrievable': True, # indicates whether there is enough info to retrieve
#     'cuisines' : ['indian'],
#     'foods' : ['nasi briyani'],
#     'location' :[],
#     'previous_state': [0,0,0], # cuisine,food,location - 0 indicates nothing, 1 indicates populated
#     'current_state': [1,1,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated
# }
# retrievable_parsed = {
#     'tokens': ['any','nice', 'nasi', 'briyani', '?'],
#     'input_text' : "Any nice nasi briyani?", # string
#     'cleansed_text' : "nice nasi briyani", # string
#     'verbs' :[],
#     'adverbs': [],
#     'nouns': ['nasi briyani'] ,
#     'adjs': ['nice'],
#     'pronouns':[]
# }
#
# responder = Responder()
# user_input = input('Key in retrievable or non_retrievable: ')
# if user_input == 'retrievable':
#     print(responder.prepare_response(retrievable_state, retrievable_parsed))
# else:
#     print(responder.prepare_response(non_retrievable_state, non_retrievable_parsed))
