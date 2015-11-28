import sys
import os
from gensim import corpora, models, similarities
import config
import tm_util
import tm_content
from tm import TopicModel

class TopicModelGen:

    def __init__(self):

        stoplist = open(config.STOPLIST, 'r')
        self.stoplist = set([word.rstrip('\n') for word in stoplist])
        stoplist.close()

        self.dictionary = None

    def createDictionary(self, dictionaryfile=config.DICTIONARY):
        if(os.path.exists(dictionaryfile)):
            print 'Dictionary ' + dictionaryfile  + ' aldready exists'
            return

        documents = []
        questionlist = tm_content.getQuestions()
        documents.extend(questionlist)
        answerlist = tm_content.getAnswers()
        documents.extend(answerlist)
        texts = tm_util.preprocessDocs(documents, self.stoplist)
        dictionary = corpora.Dictionary(texts)
        dictionary.save(dictionaryfile)
        print 'Dictionary ' + dictionaryfile + ' created.'

    def loadDictionary(self, dictionaryfile=config.DICTIONARY):
        self.dictionary = corpora.Dictionary.load(dictionaryfile)



    def createCorpus(self, postlist, corpusfile):
        if(os.path.exists(corpusfile)):
            print 'Corpus at ' + corpusfile + ' aldready exists'
            return

        if(self.dictionary == None):
            self.loadDictionary()
        texts = tm_util.preprocessDocs(postlist, self.stoplist)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(corpusfile, corpus)
        print 'Corpus at' + corpusfile + ' created.'

    def createQuestionCorpus(self, questioncorpusfile=config.QUESTIONS):
        if(os.path.exists(questioncorpusfile)):
            print 'Corpus at ' + questioncorpusfile + ' aldready exists'
            return

        questionlist = tm_content.getQuestions(savetofile=True, min20words=True)
        self.createCorpus(questionlist, questioncorpusfile)

    def createAnswerCorpus(self, answercorpusfile=config.ANSWERS):
        if(os.path.exists(answercorpusfile)):
            print 'Corpus at ' + answercorpusfile + ' aldready exists'
            return

        answerlist = tm_content.GetAnswers()
        self.createCorpus(answerlist, answercorpusfile)

    def createCombinedCorpus(self, combinedcorpusfile=config.COMBINED):
        if(os.path.exists(combinedcorpusfile)):
            print 'Corpus at ' + combinedcorpusfile + ' aldready exists'
            return

        questionlist = tm_content.getQuestions()
        answerlist = tm_content.getAnswers()
        combinedlist = questionlist + answerlist
        self.createCorpus(combinedlist, combinedcorpusfile)



    def createTopicModel(self, method, corpus, modelfile, indexfile):
        if(os.path.exists(modelfile)):
            print 'Topic Model ' + modelfile + ' aldready exists'
            return

        if(self.dictionary == None):
            self.loadDictionary()
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]

        if(method=='lda_mallet'):
            model = models.wrappers.LdaMallet(config.MALLET_PATH, corpus, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
            index = similarities.MatrixSimilarity(model[corpus])
        elif(method=='lda'):
            model = models.LdaModel(corpus_tfidf, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
            index = similarities.MatrixSimilarity(model[corpus_tfidf])
        model.save(modelfile)
        index.save(indexfile)
        print 'Topic Model ' + modelfile + ' created.'

    def createQuestionTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.QUESTIONS, modelfile=config.QUESTION_MODEL, indexfile=config.QUESTION_INDEX):
        corpus = corpora.MmCorpus(corpusfile)
        self.createTopicModel(method, corpus, modelfile, indexfile)

    def createAnswerTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.ANSWERS, modelfile=config.ANSWER_MODEL, indexfile=config.ANSWER_INDEX):
        corpus = corpora.MmCorpus(corpusfile)
        self.createTopicModel(method, corpus, modelfile, indexfile)

    def createCombinedTopicModel(self, method=config.TOPICMODEL_METHOD, corpusfile=config.COMBINED, modelfile=config.COMBINED_MODEL, indexfile=config.COMBINED_INDEX):
        corpus = corpora.MmCorpus(corpusfile)
        self.createTopicModel(method, corpus, modelfile, indexfile)

    def createUserTopicModel(self, corpusfile=config.USERS, modelfile=config.USER_MODEL, indexfile=config.USER_INDEX):
        if(os.path.exists(modelfile)):
            print 'User Topic Model ' + modelfile + ' aldready exists'
            return
        if(self.dictionary == None):
            self.loadDictionary()
        corpus = corpora.MmCorpus(corpusfile)
        model = models.LsiModel(corpus, id2word=self.dictionary, num_topics=config.NUM_TOPICS_LDA)
        index = similarities.MatrixSimilarity(model[corpus])
        model.save(modelfile)
        index.save(indexfile)
        print 'User Topic Model ' + modelfile + ' created.'

    def learn(self, createquestionmodel = False, createanswermodel = False):
        self.createDictionary()
        if(createquestionmodel):
            self.createQuestionCorpus()
            self.createQuestionTopicModel()
        if(createanswermodel):
            self.createAnswerCorpus()
            self.createAnswerTopicModel()
        self.createCombinedCorpus()
        self.createCombinedTopicModel()
        model = TopicModel(modelfile=config.CURRENT_MODEL, indexfile=config.CURRENT_INDEX)
        model.createUserCorpus()
        self.createUserTopicModel()

if __name__ == '__main__':

    if(len(sys.argv)==2):
        option = int(sys.argv[1])

    topicmodelgenerator = TopicModelGen()
    if(option==1):
        topicmodelgenerator.learn()
    elif(option==2):
        topicmodelgenerator.learn(createquestionmodel=True)
    elif(option==3):
        topicmodelgenerator.learn(createanswermodel=True)
