#step2
from gensim import corpora, models, similarities
dictionary = corpora.Dictionary.load('question.dict')
corpus = corpora.MmCorpus('question.mm')

tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50)
index1 = similarities.MatrixSimilarity(lsi[corpus_tfidf])
lsi.save('model.lsi')
index1.save('questions.index')
