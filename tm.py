import os
import pickle
from project544.base import FeatureGeneratorBase
from gensim import corpora, models, similarities
from model import Users
import config
import tm_util
import tm_content

class TopicModel(FeatureGeneratorBase):

    def __init__(self, modelfile=config.CURRENT_MODEL, indexfile=config.CURRENT_INDEX, method=config.TOPICMODEL_METHOD, corpus=config.COMBINED):
        stoplist = open(config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()
        self.corpus = corpora.MmCorpus(corpus)
        self.tfidf = models.TfidfModel(self.corpus)
        self.dictionary = self.loadDictionary()
        self.model = self.loadTopicModel(modelfile, method)
        self.index = similarities.MatrixSimilarity.load(indexfile)
        self.method = method

    def loadDictionary(self, dictionaryfile=config.DICTIONARY):
        return corpora.Dictionary.load(dictionaryfile)

    def loadTopicModel(self, modelfile, method):
        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet.load(modelfile)
        elif(method=='lda'):
            model = models.LdaModel.load(modelfile)
        return model

    def getAnswerFeatures(self, answer):
        return self.getDocumentFeatures(answer.parentid.title + " " + answer.parentid.body + " " + answer.body, None)

    def getDocumentFeatures(self, document, tags):
        document_model = None
        if(document!=None and len(document)>1):
           # print 'Reached 1'
            documenttext = tm_util.preprocessDocs([tm_util.preprocessPost(document)], self.stoplist)
            document_bow = self.dictionary.doc2bow(documenttext[0])
            #print 'Reached 2'
            document_tfidf = self.tfidf[document_bow]
            if(self.method=='lda'):
                document_model = self.model[document_tfidf]
            elif(self.method=='lda_mallet'):
             #   print 'Reached 3'
                document_model = self.model[document_bow]
        return document_model

    def getUserFeatures(self, userid):
        userdocument = tm_content.getUserAnswers(userid)
        user_features = self.getDocumentFeatures(userdocument, None)
        return user_features

    def findSimilarDocs(self, document, n=10):
        document_model = self.getDocumentFeatures(document, None)
        sims = self.index[document_model]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sims[:n]

    def createUserCorpus(self, userfile=config.USERS):
        if(os.path.exists(userfile)):
            print 'User Corpus ' + userfile + ' aldready exists'
            return

        usercorpus = []
        userslist = []
        for User in Users.select():
            user_features = self.getUserFeatures(User.id)
            if(user_features!=None):
                usercorpus.append(user_features)
                userslist.append(User.id)
        corpora.MmCorpus.serialize(userfile, usercorpus)
        userfile = open(config.USERS_LIST, 'w')
        pickle.dump(userslist, userfile)
     #   print 'User Corpus '  + userfile + ' created.'

    def getMaxDimSize(self):
        return config.NUM_TOPICS_LDA

class QuestionTopicModel(TopicModel):

    def __init__(self, modelfile=config.QUESTION_MODEL, indexfile=config.QUESTION_INDEX, method='lda_mallet', corpus=config.QUESTIONS):
        super(QuestionTopicModel, self).__init__(modelfile, indexfile, method)
        self.questions = None
        self.method = method
        with open(config.QUESTION_LIST, 'r') as fin:
            self.questions = pickle.load(fin)

    def findSimilarQuestions(self, question, n=5):
        sims = self.findSimilarDocs(question, n)
        similar = []
        for sim in sims:
            q = self.questions[sim[0]]
            similar.append((q[0], q[1].encode('utf-8')))
        print similar
        return similar
