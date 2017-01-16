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

# set up logger
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class JiakBot:

    __greeting_dict = {}
    __self_noun_desc = []
    __self_adj_desc = []
    __self_generic = []
    __generic_resp = []

    # Initializer
    def __init__(self):

        # Sets up dictionary for greetings
        greeting_corpus = json.load(open(greeting_path))
        greeting = greeting_corpus['greetings']

        for word in range(0, len(greeting)):
            greeting_key = greeting[word][0].lower()
            greeting_value = greeting[word][1]
            self.__greeting_dict[greeting_key] = greeting_value

        # Sets up self descriptions vocabulary
        self_desc_corpus = json.load(open(self_desc_path))
        self.__self_noun_desc = self_desc_corpus['noun']
        self.__self_adj_desc = self_desc_corpus['adjective']
        self.__self_adj_desc = self_desc_corpus['generic']

        # Sets up generic responses
        generic_resp_corpus = json.load(open(generic_resp_path))
        self.__generic_resp = generic_resp_corpus['generic']

    # Public function to respond
    # -----------------------------------------------------
    def respond(self, sentence):
        clean_text = self._preprocess_text(sentence)
        clean_text_blob = TextBlob(clean_text)

        pronoun, noun, adjective, verb = self._find_candidate_parts_of_speech(clean_text_blob)

        # check for comments about bot
        response = self._check_talk_about_bot(pronoun=pronoun,noun=noun,adjective=adjective)

        # check for greetings
        if not response:
            response = self._check_greeting(clean_text_blob)

        # attempt to construct a sensible response
        if not response:
            if not pronoun:
                resp = random.choice(self.__generic_resp)
            elif pronoun == 'I' and not verb:
                resp = random.choice(self.__self_generic)
            else:
                resp = self.construct_response(pronoun, noun, verb)

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

    #continue here
    def construct_response(self,pronoun, noun, verb):
        """No special cases matched, so we're going to try to construct a full sentence that uses as much
        of the user's input as possible"""
        resp = []

        if pronoun:
            resp.append(pronoun)

        # We always respond in the present tense, and the pronoun will always either be a passthrough
        # from the user, or 'you' or 'I', in which case we might need to change the tense for some
        # irregular verbs.
        if verb:
            verb_word = verb[0]
            if verb_word in ('be', 'am', 'is', "'m"):  # This would be an excellent place to use lemmas!
                if pronoun.lower() == 'you':
                    # The bot will always tell the person they aren't whatever they said they were
                    resp.append("aren't really")
                else:
                    resp.append(verb_word)
        if noun:
            pronoun = "an" if starts_with_vowel(noun) else "a"
            resp.append(pronoun + " " + noun)

        resp.append(random.choice(("tho", "bro", "lol", "bruh", "smh", "")))

        return " ".join(resp)
        # end