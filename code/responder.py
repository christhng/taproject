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
question_to_feedback_path = config['file_path']['question_to_feedback_corpus']
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
no_response_data = json.load(open(no_response_path))
question_to_feedback_data = json.load(open(question_to_feedback_path))
further_probe_data = json.load(open(further_probe_path))

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
    # responses to questions user asks when bot asks for feedback
    question_to_feedback = question_to_feedback_data['question']
    # words that encourage further probing
    further_probe_words = further_probe_data['probe_words']

    def get_response(self, state, parsed_dict):
        """
        Response controller

        Arguments:
            state (dict) - Dictionary passed from StateMachine object
            parsed (dict) - Dictionary passed from Parser object
        """

        # retrieve the input type - question, rhetoric, statement
        input_type = parsed_dict['input_type']
        if input_type == 'rhetoric':
            response = self._construct_response_to_rhetoric(parsed_dict)
        if state['retrievable']:
        # if retrievable go retrieve the biz name, location and 1 line of review
            response_dict = self._contruct_response_from_db(state, parsed_dict)
            response = response_dict['response']
            retrieved = response_dict['retrieved']
            state['retrieved'] = retrieved
            state['recommendations'] = response_dict['recommendations']
        # detect if previous statement was a recommendation
        elif state['retrieved']:
            # if bot is asking for a feedback
            # pass input_type to constructor
            r = self._construct_response_to_feedback(parsed_dict, input_type, state)
            response = r['response']
            state['retrieved'] =  r['retrieved'] # reset retrieved status
            state['post_feedback'] = r['post_feedback']
            state['recommendations'] = r['recommendations']
        elif state['post_feedback'] and input_type != 'question':
            # construct a response for the user's input right after the bot
            # has responded to the user's feedback about the most recent
            # recommendation
            r = self._construct_response_to_post_feedback(parsed_dict, input_type, state)
            # construct response
            response = r['response']
            state['post_feedback'] = r['post_feedback']
            state['recommendations'] = r['recommendations']
        # logic to construct a sensible response
        else:
            # get topic from parsed_dict - greeting, bot, user
            topic = self._get_topic(parsed_dict)
            response = AlternativeResponder(
                parsed_topic=topic,
                parsed_dict=parsed_dict,
                input_type=input_type
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
            state['recommendations'].append(result['biz_name'])
            retrieved = True
        # prepare response
        return {'response': response, 'retrieved': retrieved, 'recommendations': state['recommendations']}

    def _construct_response_to_feedback(self, parsed_dict, input_type, state):
        """
        Response generated in response to feedback given to a
        prior recommendation.

        Arguments:
            parsed_dict (dict) - Dictionary passed from Parser object
        """
        # If bot asked for feedback and user, in turn, asked a question back
        retrieved = True
        post_feedback = False
        # default response
        response = "Wah I don't understand sia, can just let me know whether my recommendation useful or not?"
        # check for intent
        intent = self._check_post_feedback_intent(parsed_dict)
        recommendations = state['recommendations']
        if intent == 'further_probe':
            retriever = Retriever()
            result = retriever.get_result(state, parsed_dict, recommendations)
            if result['biz_name']:
                response = "Ok, maybe you can try {0} instead! " \
                           "They serve {1}. " \
                           "Here's a statement someone made for {2}:\n{3} \n" \
                           "Here's a full review, " \
                           "if you bothered to read: \n{4}\n" \
                           "Is this what you are looking for?".format(result['biz_name'],
                                                                      result['category'],
                                                                      result['biz_name'],
                                                                      result['statement'],
                                                                      result['review'])
                recommendations.append(result['biz_name'])
            else:
                # no other suggestions
                response = "Sorry I can't find anything else liao!"
                retrieved = False
                post_feedback = True
        elif input_type == 'question':
            response = random.choice(self.question_to_feedback)
        # If user gave a response that could be understood as 'yes' or 'no'
        else:
            for w in parsed_dict['tokens']:
                if w in self.yes_words:
                    response = random.choice(self.yes_response)
                    retrieved = False
                    post_feedback = True
                elif w in self.no_words:
                    response = random.choice(self.no_response)
                    retrieved = False
                    post_feedback = True
        return {'response': response, 'retrieved': retrieved, 'post_feedback': post_feedback, 'recommendations': recommendations}

    def _construct_response_to_post_feedback(self, parsed_dict, input_type, state):
        """
        Response to user's input. This is only for the conversation immediately
        after the user's response to the bot's request for feedback.

        In this case, the feedback MUST have already been retrieved. This is
        the final step before state machine resets
        """
        post_feedback = True
        intent = self._check_post_feedback_intent(parsed_dict)
        if intent == 'further_probe':
            recommendations = state['recommendations']
            retriever = Retriever()
            result = retriever.get_result(state, parsed_dict, recommendations)
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
            recommendations = recommendations.append(result['biz_name'])
        elif intent == 'reset':
            # get topic from parsed_dict - greeting, bot, user
            topic = self._get_topic(parsed_dict)
            response = AlternativeResponder(
                parsed_topic=topic,
                parsed_dict=parsed_dict,
                input_type=input_type
                ).construct()
            post_feedback = False
            recommendations = []
        return {'response': response, 'post_feedback': post_feedback, 'recommendations': recommendations}

    def _check_post_feedback_intent(self, parsed_dict):
        for w in parsed_dict['tokens']:
            if w in self.further_probe_words:
                return 'further_probe'
        return 'reset'

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
