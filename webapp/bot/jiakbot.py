import logging

# import jiakbot helpers
from .state_machine import StateMachine
from .jiakbot_parser import JiakBotParser
from .responder import Responder

# set up logger
logging.basicConfig()
logger = logging.getLogger()

# INFO to switch display all logs
# WARNING to display only warning
logger.setLevel(logging.WARNING)


class JiakBot:

    state_machine = StateMachine()
    jiakbot_parser = JiakBotParser()
    responder = Responder()

    # Initializer
    def __init__(self):
        pass

    # Public function to respond
    # -----------------------------------------------------
    def respond(self, sentence):

        p = self.jiakbot_parser
        sm = self.state_machine
        r = self.responder

        response = ''

        # get the parsed dict
        parsed_dict = p.parse_input(sentence)

        # get the current state
        sm.update_state(parsed_dict)

        # print('----- ----- ----- -----')
        # print('parsed_dict:', parsed_dict)
        # print('state:',sm.state)
        # print('----- ----- ----- -----')

        # get the response
        response = r.get_response(sm.state, parsed_dict)

        return(response)
