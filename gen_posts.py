#step1
from gensim import corpora, models, similarities
import xml.etree.ElementTree
import re
import pickle
from bs4 import BeautifulSoup


e = xml.etree.ElementTree.parse('Posts.xml').getroot()
documents = []
for a in e.findall('row'):
    type = a.get('PostTypeId')  
    if(type is not None):    
        text = a.get('Body')
        soup = BeautifulSoup(text)
        text = soup.get_text()
        documents.append(text)
stoplist = set('for a of the and to in'.split())
texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1
texts = [[token for token in text if frequency[token] > 1] for text in texts]
dictionary = corpora.Dictionary(texts)
dictionary.save('posts.dict')
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('post.mm', corpus)
with open("names_posts", 'w') as fout:
    pickle.dump(documents, fout)
print "done"


