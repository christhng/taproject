# import relevant stuff here
import nltk

class Parser:

    def parse_input(self, user_input):

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
        parsed_dict['input_text'] = user_input

        from nltk.tokenize import word_tokenize
        parsed_dict['tokens'] = word_tokenize(user_input)

        from nltk import pos_tag
        tagged = pos_tag(parsed_dict['tokens'])

        parsed_dict['verbs'] = [word for word, pos in tagged \
                                if (pos == 'VB' or pos == 'VBZ' or pos == 'VBD' or pos == 'VBN' or pos == 'VBG' or pos == 'VBP')]

        parsed_dict['adverbs'] = [word for word, pos in tagged \
                                  if (pos == 'RB' or pos == 'RBR' or pos == 'RBS' or pos == 'WRB')]

        parsed_dict['nouns'] = [word for word, pos in tagged \
                                if (pos == 'NN' or pos == 'NNS' or pos == 'NNP' or pos == 'NNPS')]

        parsed_dict['adjs'] = [word for word, pos in tagged \
                               if(pos == 'JJ' or pos == 'JJR' or pos == 'JJS')]

        parsed_dict['pronouns'] = [word for word, pos in tagged \
                                   if (pos == 'PRP' or pos == 'PRP$' or pos == 'WP' or pos == 'WP$')]

        import re
        words = [w for w in parsed_dict['tokens'] if re.search('^[a-z]+$', w)]

        from nltk.corpus import stopwords
        stop_list = stopwords.words('english')
        parsed_dict['cleansed_text'] = [w for w in words if w not in stop_list]


        #######################################################################
        return parsed_dict

p = Parser()
output = p.parse_input('their quick brown fox jumped over our lazy dog slowly.')

print(output)