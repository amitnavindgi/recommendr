import util
from nltk import word_tokenize
from collections import defaultdict

def preprocessPost(post):
    return util.stripTags(post).replace('\n', ' ').replace('\r', ' ')

def preprocessDocs(documents, stoplist):
    texts = [[word for word in word_tokenize(document.lower()) if word not in stoplist] for document in documents]

    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1 and len(token) > 2 ] for text in texts]

    return texts
