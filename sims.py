#step3
import pickle
from gensim import corpora, models, similarities
dictionary = corpora.Dictionary.load('question.dict')
corpus = corpora.MmCorpus('question.mm')

tfidf = models.TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

query = "what is a linked list"
query_bow = dictionary.doc2bow(query.lower().split())
query_tfidf = tfidf[query_bow]


lsi = models.LsiModel.load('model.lsi')
query_model = lsi[query_tfidf]
index = similarities.MatrixSimilarity.load('questions.index')


sims = index[query_model] 
sims = sorted(enumerate(sims), key=lambda item: -item[1])

with open('names', 'r') as doc:
    documents = pickle.load(doc)

for sim in sims[:5]:
    print("\nSimilarity Score: " + str(sim[1]) + ', Id: ' + str(sim[0]) + '\nQuestion: ' + documents[sim[0]].encode('utf-8'))
    print("------------------------------------------------------------------------------------")