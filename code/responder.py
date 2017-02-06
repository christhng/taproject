import json
import random
from retriever import Retriever


class TopicRetriever:
    """Topic parser class

    Attributes:
        parsed_dict (dict) - dictionary of parsed words from Parser object
    """
    bot_corpus = ['you', 'jiakbot', 'bot']
    user_corpus = ['i', 'me', 'i\'m', 'im', 'mine']
    greeting_corpus = json.load(open('../corpus/greetings.json'))['greetings']

    def __init__(self, parsed_dict):
        self.parsed_dict = parsed_dict

    def retrieve(self):
        """Retrieve topic in order of importance.

        Order of importance:
            1) greeting
            2) bot reference
            3) user reference
        """
        assert isinstance(parsed_dict, dict)

        greetings = {}
        for g in self.greeting_corpus:
            greetings[g[0].lower()] = g[1]
        for key in greetings.keys():
            if key in self.parsed_dict['tokens']:
                return 'greeting'

        retrieve_bot_ref = [w for w in self.bot_corpus
                            if w in self.parsed_dict['pronouns'] or
                            w in self.parsed_dict['nouns']]
        if retrieve_bot_ref:
            return 'bot'

        retrieve_user_ref = [w for w in self.user_corpus
                            if w in self.parsed_dict['pronouns']]
        if retrieve_user_ref:
            return 'user'


class AlternativeResponder:
    """Alternative response class

    Attributes:
        parsed_topic - A string representing the alternative topic of interest
        based on the parsed sentence
        topics - List of available topics
    """
    topics = ['bot', 'user', 'greeting']
    responses = {
        'bot': 'You are talking about me',
        'user': 'You are talking about yourself',
        'greeting': 'Hello back',
    }

    def __init__(self, parsed_topic):
        """Return AlternativeResponder object which will respond to
        a particular topic

        Available topics:
            bot - about the bot itself
            user - about the user
            greeting - general greetings
        """
        self.parsed_topic = parsed_topic

    def check_topic(self):
        """Checks if parsed_topic argument is in list of available topics"""
        if self.parsed_topic in self.topics:
            return True
        return False

    def construct(self):
        """Constructs alternative response

        Arguments:
            parsed_topic (string) - string which represents a topic that the
            bot can comprehend
        """
        if self.check_topic():
            response = responses[self.parsed_topic]
        else:
            response = "I don't quite understand you"
        return response


class Responder:
    """Reponse constructor class

    Steps taken to create a response:
        1) Check if results are retrievable
        2a) If retrievable, Retrieve results from Retriever object
            2a-1) Check that there is content retrieved in results dictionary
            2a-2) Return response accordingly
        2b) If not retrievable, use AlternativeResponder object to generate
        response based on topic
    """

    def check_retrieve(self, result):
        """Checks whether response dict is empty

        Arguments:
            result (dict) - results retrieved using Retriever object
        """
        for key in result.keys():
            if not result[key]:
                return False # If result[key] is empty
        return True

    def response_constructor(self, result):
        """Constructs response

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
        """Response generated from a result that was successfully
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

    def prepare_reponse(self, state, parsed):
        """Response controller

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
            response = AlternativeResponder(parsed_topic=topic).construct()
        return response
