__author__ = 'sandeep'

import xml.etree.ElementTree
import re
import pickle
import util
from sklearn.linear_model import Perceptron
from sklearn.feature_extraction import FeatureHasher

def testPredictEval(up, tgen, kSet, evaluationpost):

   # query = query[0:9]
    pak = dict((k,0) for k in kSet)
    mrr = 0


        #print("labels="+str(answerUserIds).strip('[]'))

   for i, userId in enumerate(predictions):
       if userId in answerUserIds:
           mrr += 1/float(i+1)
           break

   pakpq = dict((k,0) for k in kSet)
   for k in kSet:
       present = False
       for userId in answerUserIds:
           if userId in predictions[:k]:
               pak[k] += 1
               pakpq[k] += 1

               # userAnswerMap = dict((ans.owneruserid.id, ans) for ans in answers if ans.owneruserid is not None and ans.score > 0)
               # for k in kSet:
               #     rel = [userAnswerMap[userId].score for userId in predictions[:k] if userId in userAnswerMap]

               #print("PAK per question for {0} = {1}".format(question.id, repr(pakpq)))

    # normalize
    queryCount = 100
    mrr /= queryCount
    pak = [(k, count/float(k*queryCount)) for k, count in pak.items()]
    return (pak, mrr)

e = xml.etree.ElementTree.parse('Posts.xml').getroot()
posts = {}
with open('tm_out', 'r') as doc:
    documents = pickle.load(doc)
for a in e.findall('row'):
    tags = a.get('Tags')
    id = a.get('Id')
    type = a.get('PostTypeId')
    user = a.get('OwnerUserId')

    if(id in posts):
        cs = posts[id]
    else:
        cs = ""
    tags = [m.group(1) for m in re.finditer(r'\<([^\>]*)\>', tags)]
    for tag in tags:
        cs += "\t" + tag
    if(id in documents):
        for items in documents[id]:
            cs += "\t" + str(items[0])
    posts[id] = cs

evaluationposts = []
for a in posts:
    type = a.get('PostTypeId')
    pId = a.get("ParentId")
    user = a.get('OwnerUserId')
    length = a.get('Length')
    accepted = a.get('Accepted')
    ownerrep = a.get('Ownerreputation')
    score = a.get('Score')
    if(type == '2'):
        if(user is not None):
            for b in posts:
                if b.get("ParentTd") == a.get('Id') and a.get('forevaluation') == 1:
                    evaluationposts.append(a+b)
set = [1,5,10]
methods = {
 #       "Topic Modelling": (config.USER_PREDICTOR_TM, TopicModel),
        "Post Tags": (TagFeatureGen),
        "Combined": (TagTMFeatureGen)
    }

results = []
for name, (upFilename, tgenClass) in methods.items():
    for evaluationpost in evaluationposts:
        file = open(upFilename, "r")
        up = pickle.load(file)
        file.close()
        tgen = tgenClass()
        results[name] = testPredictEval(up, tgen, set, evaluationpost)
