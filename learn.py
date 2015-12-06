import xml.etree.ElementTree
import re
import pickle
from gensim import corpora, models, similarities
from sklearn import linear_model
from sklearn.datasets import make_classification
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction import FeatureHasher
import gensim
from bs4 import BeautifulSoup

clf = Perceptron()
dictionary = corpora.Dictionary.load('question.dict')
corpus = corpora.MmCorpus('question.mm')
e = xml.etree.ElementTree.parse('Posts.xml').getroot()
tfidf = models.TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

questions = {}
with open('tm_out', 'r') as doc:
    documents = pickle.load(doc)
for a in e.findall('row'):
    tags = a.get('Tags')
    id = a.get('Id')
    type = a.get('PostTypeId')
    user = a.get('OwnerUserId')
    if(type == '1'):
        if(id in questions):
                cs = questions[id]
        else:
            cs = ""
        tags = [m.group(1) for m in re.finditer(r'\<([^\>]*)\>', tags)]        
        for tag in tags:
            cs += "\t" + tag
        if(id in documents):
            for items in documents[id]:
                cs += "\t" + str(items[0])
        questions[id] = cs
y = []
X = []
dictionary = corpora.Dictionary.load('question.dict')
mm = corpora.MmCorpus('question.mm')
d = {}
lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=50)
for a in e.findall('row'):
    tags = []
    type = a.get('PostTypeId')
    pId = a.get("ParentId")
    user = a.get('OwnerUserId')    
    if(type == '2'):
        if(user is not None):
            tags.append(questions[pId])
    text = a.get('Body')
    s = a.get('Score')
    c = a.get('CommentCount')
    id = a.get('Id')
    y.append(id)
    X.append(tags)
    x.append(('s', float(s)/100.0))
    x.append(('c', float(c)/100.0))
X = featureHasher.transform(X)
y = numpy.array(y)
model = clf.partial_fit(X, y, classes=allClasses)
with open("tags.model", 'w') as fout:
    pickle.dump(model, fout)
for a in e.findall('row'):
    tags = []
    type = a.get('PostTypeId')
    pId = a.get("ParentId")
    user = a.get('OwnerUserId')    
    if(type == '2'):
        if(user is not None):
            tags.append(questions[pId])
    text = a.get('Body')
    s = a.get('Score')
    c = a.get('CommentCount')
    soup = BeautifulSoup(text)
    text = soup.get_text()
    query_bow = dictionary.doc2bow(text.lower().split())
    id = a.get('Id')
    y.append(id)
    X.append(tags)
    X.append(lda[query_bow])
    x.append(('s', float(s)/100.0))
    x.append(('c', float(c)/100.0))
X = featureHasher.transform(X)
y = numpy.array(y)
model = clf.partial_fit(X, y, classes=allClassesy)
with open("postctopic.model", 'w') as fout:
    pickle.dump(model, fout)
        