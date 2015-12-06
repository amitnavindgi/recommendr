from gensim import corpora, models, similarities
import gensim
import xml.etree.ElementTree
import re
import pickle
from bs4 import BeautifulSoup
dictionary = corpora.Dictionary.load('question.dict')
mm = corpora.MmCorpus('question.mm')
d = {}
lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=50)
e = xml.etree.ElementTree.parse('Posts.xml').getroot()
for a in e.findall('row'):
    text = a.get('Body')
    soup = BeautifulSoup(text)
    text = soup.get_text()
    query_bow = dictionary.doc2bow(text.lower().split())
    id = a.get('Id')
    print(id)
    print (lda[query_bow])
    d[id] = lda[query_bow]
with open("tm_out", 'w') as fout:
    pickle.dump(d, fout)