import sqlite3
import nltk
from nltk import word_tokenize, RegexpTokenizer
from nltk.stem.porter import *
from nltk.corpus import stopwords

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
        self.__reviews_db = "/home/brij/smu/TextAnalytics/project/taproject/database/jiakbot.db"
        self.__conn = sqlite3.connect( self.__reviews_db )
        self.__out_base = "/home/brij/smu/TextAnalytics/project/taproject/corpus/reviews/"
        self.initialize()

    def initialize( self ):
        stopword_list = stopwords.words( "english" )
        stopword_addendum = [ ".", ",", "a" ]
        self.run['stopwords' ] = stopword_list + stopword_addendum

        self.__training_doc_limit = 2000

    def generateDocs( self ):
        sql = """select description from reviews"""
        c = self.__conn.cursor()
        c.execute( sql )
        i = 0
        for row in c.fetchall() :
            doc = self.__out_base + str(i)+".txt"
            fh = open( doc, "w", encoding="utf8" )
            fh.write( row[0] )
            fh.close()
            i += 1
            self.__docs.append( doc )
            if i == self.__training_doc_limit: break

    def readCorpus( self ):
        unique_word_set = set()

        for file in self.__docs :
            words = []
            fh = open( file, "r", encoding="utf8" )

            for line in fh.readlines():
                words.append( self.tokenize( line ) )
            fh.close()
            a = [ i for x in words for i in x ]
            self.__corpus.append( a )
        del unique_word_set

    def tokenize( self, sent ):
        if not 'tokenizer' in self.run : 
            self.run['tokenizer'] = RegexpTokenizer( '\w+|[\$\d\.]+' )
        return self.run['tokenizer'].tokenize( sent )
    
    def preprocess( self, corpus ):
        ###change words to lower case
        corpus = [ [ word.lower() for word in doc ] 
                                                    for doc in corpus ]

        #####remove stopwords
        corpus = [ [ word for word in doc if word not in 
                            self.run['stopwords'] ] for doc in corpus ]

        ####perform stemming
        stemmer = PorterStemmer()
        corpus = [ [ stemmer.stem(word) for word in doc ] 
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

    def perform_lda( self ):
        #####Calculate topics distribution on the corpus using LDA( Latent Dirichlet Analysis )
        self.run['lda'] = models.ldamodel.LdaModel( self.run['docs_bow'],
                                                    num_topics = 20, 
                                                    id2word = self.run['dictionary'], 
                                                    passes = 2 )

        #print( self.run['lda'].print_topics( num_topics=100, num_words=3 ) )
        #print( self.run['lda'].get_topic_terms( aa[1][0][0] ) )

        self.run.setdefault( 'doc_topics', {} )
        for index, doc_bow in enumerate(self.run['docs_bow']) :
            topic_tuple = self.run['lda'][doc_bow] ##vector of topic tuples ( topicid, prob )

            topics = []
            sorted_topic_terms = sorted( self.run['lda'].get_topic_terms( topic_tuple[0][0] ), 
                                                                        key=lambda item : -item[1] )
            for word_tuple in sorted_topic_terms[:5]:
                topics.append( self.get_token( word_tuple[0] ) )
            self.run['doc_topics'][index] = topics

    def get_token( self, id ):
        for item in self.run['dictionary'].iteritems() :
            if item[0] == id :
                return( item[1] )

    def get_similarity_topics( self, stmt ):
        stmt_vec = []
        stmt_vec.append( self.tokenize( stmt ) )
        self.preprocess( stmt_vec )
        stmt_vsm = [ i for doc in stmt_vec for i in self.get_tf_idf( self.run['dictionary'].doc2bow(doc) ) ]
        similar_docs = self.get_tf_idf_sim( stmt_vsm )
        for similar_doc_tuple in similar_docs[:1]:      ###considering only most similar doc 
            similar_doc = similar_doc_tuple[0]
            likely_topic = self.run['doc_topics'][similar_doc]
            print( likely_topic )
        

a = ContextGeneration()
a.generateDocs()

a.readCorpus()
a.prepare_data()
a.perform_lda()
a.get_similarity_topics( "i love food and coffee" )
