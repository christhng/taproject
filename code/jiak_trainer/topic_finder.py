import sqlite3
import nltk
from nltk import word_tokenize, RegexpTokenizer
from nltk.stem.porter import *
from nltk.corpus import stopwords
import configparser
import os
from time import time, strftime, localtime, sleep
import logging
import gensim
from gensim import corpora,models, similarities


class ContextGeneration:
    __reviews_db = ""
    __conn = ""
    __docs = []
    __corpus = []
    __training_doc_limit = ""

    def __init__( self ) :
        self.run = {}
        self.cwd = os.getcwd()
        self.config_file = self.cwd + "/../../config_app/app_config.ini"
        self.config_section = "topic_trainer"
        self.logger=""

        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read( self.config_file )
        self.config = config

        self.initialize_logger( config.get( self.config_section, "train_logs" ) )


        self.__reviews_db = config.get( self.config_section, "reviews_db" )
        self.__conn = sqlite3.connect( self.__reviews_db )

        self.__out_base = config.get( self.config_section, "out_base" )

        self.initialize()


    def initialize_logger( self, log_direc ) :
        logger = logging.getLogger( "TOPIC_TRAINER" )
        logger.setLevel( logging.DEBUG )

        logfile = os.path.splitext( __file__ )[0] + "_" + strftime("%Y%m%d%Y%H%M%S", localtime() ) + ".log"
        fh = logging.FileHandler( log_direc + "/" + logfile )
        fh.setLevel( logging.DEBUG )
        formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
        fh.setFormatter( formatter )
        logger.addHandler( fh )
        self.logger = logger

    def initialize( self ):
        stopword_list = stopwords.words( "english" )
        stopword_addendum = [ ".", ",", "a" ]
        self.run['stopwords' ] = stopword_list + stopword_addendum

        self.__training_doc_limit = self.config.get( self.config_section, "training_doc_limit" ) or -1
        self.generateDocs()
        self.readCorpus()
        self.prepare_data()

    def generateDocs( self ):
        sql = """select description from reviews order by review_id limit """ + str( self.__training_doc_limit )
        print( sql )
        c = self.__conn.cursor()
        c.execute( sql )
        i = 1
        for row in c.fetchall() :
            doc = self.__out_base + "/" + str(i)+".txt"
            i += 1
            self.__docs.append( doc )

            """check if the doc already exists; in which case no need to create a new file.
            This action can be overwritten by enabling force_write option in config file"""

            if self.config.get( self.config_section, "force_write" ) :
                if os.path.isfile( doc ) :
                    #self.logger.info( "Skipping file = " + doc )
                    continue   ##skip writing this doc if it alread exists

            self.logger.info( "Writing doc = " + doc )
            fh = open( doc, "w", encoding="utf8" )
            fh.write( row[0] )
            fh.close()

    def readCorpus( self ):
        #index = 0
        for file in self.__docs :
            #index += 1
            words = []
            fh = open( file, "r", encoding="utf8" )

            for line in fh.readlines():
                words.append( self.tokenize( line ) )
            fh.close()
            a = [ i for x in words for i in x ]
            self.__corpus.append( a )
            #if index == 100: break

    def tokenize( self, sent ):
        if not 'tokenizer' in self.run :
            self.run['tokenizer'] = RegexpTokenizer( '\w+|[\$\d\.]+' )
        return self.run['tokenizer'].tokenize( sent )

    def word_generator( self, word ):
        self.__counter.setdefault( word, 1 )

        if self.__counter[ word ] <=2 :
            self.__counter[ word ] += 1
            return word
        else:
            return ""

    def doc_generator( self, doc ):
        self.__counter = {}
        return doc

    def preprocess( self, corpus ):
        ###change words to lower case
        corpus = [ [ word.lower() for word in doc ]
                                                    for doc in corpus ]

        #####remove stopwords

        corpus = [ [ word for word in doc if word not in
                            self.run['stopwords'] ] for doc in corpus ]

        ####perform stemming
        #stemmer = PorterStemmer()
        #corpus = [ [ stemmer.stem(word) for word in doc ] for doc in corpus ]
        corpus = [ [ self.word_generator( word ) for word in self.doc_generator( doc )  ]
                                    for doc in corpus ]
        return corpus

    def get_tf_idf( self, bow ):
        if not 'tfidf' in self.run :
            self.run['tfidf'] = models.TfidfModel( self.run['docs_bow'] )
        return self.run['tfidf'][bow]

    def get_tf_idf_sim( self, tfidf ):
        if not 'similarity_index' in self.run:
            self.run['similarity_index'] = similarities.SparseMatrixSimilarity(
                                                self.run['tfidf_bow'], len(self.run['dictionary'] ) )
        return sorted( enumerate(self.run['similarity_index'][tfidf]), key=lambda item: -item[1] )

    def prepare_data( self ):
        self.__corpus = self.preprocess( self.__corpus )

        self.run['dictionary'] = corpora.Dictionary( self.__corpus )

        self.run['docs_bow'] = [ self.run['dictionary'].doc2bow(doc) for doc in self.__corpus ]

        self.run['tfidf_bow'] = [ self.get_tf_idf(bow) for bow in self.run['docs_bow'] ]
        #del self.__corpus

    def persist_topic( self, doc_id, topic ):
        c = self.__conn.cursor()
        sql = 'update reviews set topic = "' + topic + '" where review_id = ' + str(doc_id)

        self.logger.info( sql + "\n" )
        c.execute( sql )
        self.__conn.commit()

    def perform_lda( self ):
        
        #####Calculate topics distribution on the corpus using LDA( Latent Dirichlet Analysis )

        num_passes = int( self.config.get( self.config_section, "lda_passes" ) )
        topics_count = int( self.config.get( self.config_section, "num_topics" ) )

        lda = models.ldamodel.LdaModel(
                                      self.run['docs_bow'],
                                      num_topics = topics_count,
                                      id2word = self.run['dictionary'],
                                      passes = num_passes )

        self.run.setdefault( 'doc_topics', {} )

        """At this point we have trained the lda and can be used to predict topic for each doc"""
        for index, doc_bow in enumerate(self.run['docs_bow']) :
            topic_vec = lda[doc_bow] ##vector of topic tuples ( topicid, prob )

            topics = []
            most_likely_topic_tuple = topic_vec[0]
            most_likely_topicid = most_likely_topic_tuple[0]

            sorted_topic_terms = sorted( lda.get_topic_terms( most_likely_topicid ),
                                          key=lambda item : -item[1] )

            for word_tuple in sorted_topic_terms[:topics_count]:
                topics.append( self.get_token( word_tuple[0] ) )

            self.logger.info( "Doc Index : " + str(index + 1) )
            self.logger.info( [ self.get_token(i[0]) for i in doc_bow ] )
            self.logger.info( topics )

            self.run['doc_topics'][index+1] = topics
            self.persist_topic( index+1, "|".join(topics ) )

    def get_token( self, id ):
        for item in self.run['dictionary'].iteritems() :
            if item[0] == id :
                return( item[1] )

    def get_similar_docs( self, stmt, ndocs=1 ):
        stmt_vec = []
        stmt_vec.append( self.tokenize( stmt ) )
        self.preprocess( stmt_vec )
        stmt_vsm = [ i for doc in stmt_vec for i in self.get_tf_idf( self.run['dictionary'].doc2bow(doc) ) ]
        similar_docs = self.get_tf_idf_sim( stmt_vsm )
        print( similar_docs[:ndocs] )

        
        #for similar_doc_tuple in similar_docs[:ndocs]:      ###considering only most similar doc
            #print( self.run['tfidf_bow'][similar_doc_tuple[0]] )
            #print( self.run['docs_bow'][similar_doc_tuple[0]] )
            #for t in self.run['tfidf_bow'][similar_doc_tuple[0]]:
                #print( similar_doc_tuple[0], t[0], self.run['dictionary'][t[0]], t[1] )
        
        return similar_docs[:ndocs]


    def get_topics( self, stmt = "", docs = [] ):
        
        print( "stmt is -->", stmt )
        if len( docs ) == 0:
            if( stmt == "" ):
                return ""
            else:
                docs = self.get_similar_docs( stmt )
        
        c = self.__conn.cursor()
        topics = []
        for similar_doc_tuple in docs:
            doc_id = similar_doc_tuple[0]
            sql = """select topic from reviews where review_id=""" + str(doc_id+1)
            c.execute( sql )

            for row in c.fetchall():
                topics.append( row[0].split("|") )

        print( topics )

    def get_doc( self, docid ):
        return self.__corpus.fileids( docid )






if __name__ == "__main__":
    a = ContextGeneration()
    #a.perform_lda()
    a.get_similar_docs( "I love food and coffee", 1 )
    a.get_topics( "I love food and coffee" )
    a.get_topics( "chicken is even better" )
