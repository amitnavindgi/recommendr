import xml.etree.ElementTree
import re
import pickle
e = xml.etree.ElementTree.parse('Posts.xml').getroot()
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
for a in e.findall('row'):
    type = a.get('PostTypeId')
    pId = a.get("ParentId")
    user = a.get('OwnerUserId')    
    if(type == '2'):
        if(user is not None):
            print (user + questions[pId])

        
                