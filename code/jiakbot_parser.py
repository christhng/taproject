# import relevant stuff here
import nltk
import re


class JiakBotParser:
    def parse_input(self, user_input):
        parsed_dict = {
            'tokens': [],
            'input_text': None,  # string
            'cleansed_text': None,  # string
            'verbs': [],
            'adverbs': [],
            'nouns': [],
            'adjs': [],
            'pronouns': [],
            'is_question':False
        }

        #######################################################################
        # insert code to parse here
        parsed_dict['input_text'] = user_input

        ## expand contractions
        #cList = {
        #    "didn\'t": "did not",
        #    "don\t": "do not"
        #}
        #c_re = re.compile('(%s)' % '|'.join(cList.keys()))

        #def expandContractions(user_input, c_re=c_re):
        #    def replace(match):
        #        return cList[match.group(0)]

        #    return c_re.sub(replace, user_input)

        #expand_input = expandContractions(user_input)

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
                               if (pos == 'JJ' or pos == 'JJR' or pos == 'JJS')]

        parsed_dict['pronouns'] = [word for word, pos in tagged \
                                   if (pos == 'PRP' or pos == 'PRP$' or pos == 'WP' or pos == 'WP$')]

        from nltk.corpus import stopwords
        stop_list = stopwords.words('english')
        words = [w for w in parsed_dict['tokens'] if re.search('^[a-z]+$', w)]
        parsed_dict['cleansed_text'] = [w for w in words if w not in stop_list]

        #######################################################################
        return parsed_dict
