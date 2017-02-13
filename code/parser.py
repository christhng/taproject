# import relevant stuff here
import nltk
import re

class Parser:

    def parse_input(self, input):

        parsed_dict = {
            'tokens': [],
            'input_text' : None, # string
            'cleansed_text' : None, # string
            'verbs' :[],
            'adverbs': [],
            'nouns': [] ,
            'adjs': [],
            'pronouns':[]
        }

        #######################################################################

        # insert code to parse here
        from nltk.tokenize import word_tokenize
        tokens = word_tokenize(self)

        from nltk import pos_tag
        parsed_dict = pos_tag(tokens)

        #######################################################################
    return parsed_dict
