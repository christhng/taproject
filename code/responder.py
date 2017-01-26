#import your libraries
from retriever import Retriever

class Responder:

    def prepare_reponse(self,state,parsed):

        response = ''

        # if retrievable go retrieve the biz name, location
        # and 1 line of review
        if state['retrievable'] == True:
            retriever = Retriever()
            result = retriever.get_result(state,parsed)

            # prepare response
            return response
        else:
            # flags to indicate the stuff the user just input
            about_bot = False
            about_user = False
            about_greeting = False
            about_vague = False

            # Analyze the content and sets the appropriate flag

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

