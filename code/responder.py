#import your libraries
from retriever import Retriever
import json
import random

class Responder:

    def check_retrieve(self, result):
        for key in result.keys():
            if not result[key]:
                return False    # If result[key] is empty
        return True

    def response_constructor(self, result):
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
            print("Response constructor only accepts %s \
            argument. Instead, %s was used." % (str(type(dict())),
                                                str(type(result))))

    def prepare_reponse(self,state,parsed):

        response = ''

        # if retrievable go retrieve the biz name, location
        # and 1 line of review
        if state['retrievable'] == True:
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
        else:
            # flags to indicate the stuff the user just input
            about_bot = False
            about_user = False
            about_greeting = False
            about_vague = False

            # Analyze the content and sets the appropriate flag

            # Hard code lists of references. Eventually can use text
            # classification to sieve out reference classes (bot, greeting etc.)

            # 1) about_bot
            bot_corpus = ['you', 'jiakbot', 'bot'] # words referring to bot
            retrieve_bot_ref = [w for w in bot_list if w in parsed['pronouns'] or w in parsed['nouns']]
            if retrieve_bot_ref:
                about_bot = True

            # 2) about_user
            me_corpus = ['i', 'me', 'i\'m', 'im', 'mine']
            retrieve_me_ref = [w for w in me_list if w in parsed['pronouns']]
            if retrieve_me_ref:
                about_user = True

            # 3) about_greeting
            greeting_corpus = json.load(open('../corpus/greetings.json'))
            greeting_corpus = greeting_corpus['greetings']
            greetings = {}
            for g in greeting_corpus:
                greetings[g[0].lower()] = g[1]
            for key in greetings.keys():
                if key in parsed['tokens']:
                    about_greeting = True

            # 4) about_vague


        # if talking about bot eg. 'you are an idiot'
        if about_bot:
            # prepare the response
            response = 'You are talking about me'

        elif about_user:
            response = 'You are talking about yourself'

        elif about_greeting:
            response = 'Hello back'

        elif about_vague:
            response = 'Can you elaborate more about _____ '

        else:
            response = "I don't quite understand you"

        return response
