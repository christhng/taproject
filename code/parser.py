# import relevant stuff here
import nltk
import re
from nltk.tokenize import word_tokenize
from nltk import pos_tag

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
        tokens = word_tokenize(self)
        tokens_words_only = [w for w in tokens if re.search('^[a-z]+$', w)]

        parsed_dict = pos_tag(tokens_words_only)

        parsed_dict['tokens'] = ['']

        #######################################################################
        return parsed_dict
