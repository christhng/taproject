import configparser
import json
import random
import logging
from textblob import TextBlob
# Set up
# ---------------------------------------------------------
config_file_path = '../config_app/app_config.ini'

# Read in the config in the auth files
config = configparser.ConfigParser()
config.read(config_file_path)

# read in the corpus paths
greeting_path = config['file_path']['greeting_corpus']
self_desc_path = config['file_path']['self_description_corpus']
generic_resp_path = config['file_path']['generic_response_corpus']
singlish_ending_path = config['file_path']['singlish_ending_corpus']

# set up logger
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

class JiakBot:

    __greeting_dict = {}
    __self_noun_desc = []
    __self_adj_desc = []
    __self_generic = []
    __generic_resp = []
    __singlish_emphasis_ending = []
    __singlish_question_ending = []
    __singlish_reluctant_ending = []

    # Initializer
    def __init__(self):

        # Sets up dictionary for greetings
        greeting_corpus = json.load(open(greeting_path))
        greeting = greeting_corpus['greetings']

        for word in range(0, len(greeting)):
            greeting_key = greeting[word][0].lower()
            greeting_value = greeting[word][1]
            self.__greeting_dict[greeting_key] = greeting_value

        # Set up self descriptions vocabulary
        self_desc_corpus = json.load(open(self_desc_path))
        self.__self_noun_desc = self_desc_corpus['noun']
        self.__self_adj_desc = self_desc_corpus['adjective']
        self.__self_adj_desc = self_desc_corpus['generic']

        # Set up generic responses
        generic_resp_corpus = json.load(open(generic_resp_path))
        self.__generic_resp = generic_resp_corpus['generic']

        # Set up Singlish ending
        singlish_ending_corpus = json.load(open(singlish_ending_path))
        self.__singlish_emphasis_ending = singlish_ending_corpus['emphasis']
        self.__singlish_question_ending = singlish_ending_corpus['question']
        self.__singlish_reluctant_ending = singlish_ending_corpus['reluctant']

    # Public function to respond
    # -----------------------------------------------------
    def respond(self, sentence):
        clean_text = self._preprocess_text(sentence)
        clean_text_blob = TextBlob(clean_text)

        logger.info("Cleansed sentence: '%s'", clean_text_blob)

        pronoun, noun, adjective, verb = self._find_candidate_parts_of_speech(clean_text_blob)

        # check for comments about bot
        response = self._check_talk_about_bot(pronoun=pronoun,noun=noun,adjective=adjective)

        # check for greetings
        if not response:
            response = self._check_greeting(clean_text_blob)

        # attempt to construct a sensible response
        if not response:
            if not pronoun:
                response = random.choice(self.__generic_resp)
            elif pronoun == 'I' and not verb:
                response = random.choice(self.__self_generic)
            else:
                response = self._construct_response(pronoun, noun, verb)

        # Falls into nothing that bot recognize. return random stuff.
        if not response:
            response = random.choice(self.__generic_resp)

        logger.info("Returning phrase '%s'", response)

        return(response)

    # Private functions
    # -----------------------------------------------------
    # Preprocess the text
    def _preprocess_text(self ,sentence):
        """Handle some weird edge cases in parsing, like 'i' needing to be capitalized
        to be correctly identified as a pronoun"""
        cleaned = []
        words = sentence.split(' ')
        for w in words:
            if w == 'i':
                w = 'I'
            if w == "i'm":
                w = "I'm"
            cleaned.append(w)

        return ' '.join(cleaned)

    # POS tagger
    def _find_candidate_parts_of_speech(self, parsed):
        """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
        Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
        pronoun = None
        noun = None
        adjective = None
        verb = None
        for sent in parsed.sentences:
            pronoun = self._find_pronoun(sent)
            noun = self._find_noun(sent)
            adjective = self._find_adjective(sent)
            verb = self._find_verb(sent)
        logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun, noun, adjective, verb)
        return pronoun, noun, adjective, verb

    def _find_pronoun(self,sent):
        """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
        pronoun is found in the input"""
        pronoun = None

        for word, part_of_speech in sent.pos_tags:
            # Disambiguate pronouns
            if part_of_speech == 'PRP' and word.lower() == 'you':
                pronoun = 'I'
            elif part_of_speech == 'PRP' and word == 'I':
                # If the user mentioned themselves, then they will definitely be the pronoun
                pronoun = 'You'
        return pronoun

    # end

    def _find_verb(self,sent):
        """Pick a candidate verb for the sentence."""
        verb = None
        pos = None

        for word, part_of_speech in sent.pos_tags:
            if part_of_speech.startswith('VB'):  # This is a verb
                verb = word
                pos = part_of_speech
                break
        return verb, pos

    def _find_noun(self,sent):
        """Given a sentence, find the best candidate noun."""
        noun = None

        if not noun:
            for w, p in sent.pos_tags:
                if p == 'NN':  # This is a noun
                    noun = w
                    break
        if noun:
            logger.info("Found noun: %s", noun)

        return noun

    def _find_adjective(self,sent):
        """Given a sentence, find the best candidate adjective."""
        adj = None
        for w, p in sent.pos_tags:
            if p == 'JJ':  # This is an adjective
                adj = w
                break
        return adj

    def _check_talk_about_bot(self,pronoun,noun,adjective):
        response = None
        if pronoun == 'I' and (noun or adjective):
            if noun:
                response = random.choice(self.__self_noun_desc).format(**{'noun':noun})
            else:
                response = random.choice(self.__self_adj_desc).format(**{'adjective': adjective})
        return response

    def _check_greeting(self,sent):
        """If any of the words in the user's input was a greeting, return a greeting response"""
        for word in sent.words:
            if word.lower() in self.__greeting_dict.keys():
                return random.choice(self.__greeting_dict[word.lower()])

    def _starts_with_vowel(self,word):
        """Check for pronoun compability -- 'a' vs. 'an'"""
        return True if word[0] in 'aeiou' else False

    #continue here
    def _construct_response(self,pronoun, noun, verb):
        """No special cases matched, so we're going to try to construct a full sentence that uses as much
        of the user's input as possible"""
        response = []

        if pronoun:
            response.append(pronoun)

        if verb:
            response.append('got')
            verb_word = verb[0]
            response.append(verb_word)

        if noun:
            response.append(noun)

        response.append(random.choice(self.__singlish_question_ending))

        return " ".join(response)
        # end