import bs4
from bs4 import BeautifulSoup
import nltk
from nltk import sent_tokenize, word_tokenize, pos_tag_sents, pos_tag
from nltk.corpus import conll2000

from nltk import ChunkParserI, TrigramTagger
from nltk.chunk import tree2conlltags, conlltags2tree

class SimpleChunkParser(ChunkParserI):
    def __init__(self, trainingChunkedSents):
        trainingData = [
            [(posTag, bioTag) for word, posTag, bioTag in tree2conlltags(chunkedSent)]
            for chunkedSent in trainingChunkedSents
        ]
        self.tagger = TrigramTagger(trainingData)

    def parse(self, sent):
        posTags = [posTag for (word, posTag) in sent]
        bioTags = [bioTag for (posTag, bioTag) in self.tagger.tag(posTags)]
        chunkedSent = [(word, posTag, bioTag) for ((word, posTag), bioTag) in zip(sent, bioTags)]
        return conlltags2tree(chunkedSent)

def stripTags(html):
    return BeautifulSoup(html).getText()

def htmlSentTokenize(html, containerTags = ("ul", "li", "ol", "[document]")):
    textList = []
    def recur(node):
        if isinstance(node, bs4.NavigableString):
            textList.append(node.string)
        elif  isinstance(node, bs4.Tag) and node.name not in containerTags:
            textList.append(node.getText())
        else:
            for child in node.children:
                recur(child)
    soup = bs4.BeautifulSoup(html)
    recur(soup)
    return [
        sent
        for text in textList if len(text.strip()) > 0
        for sent in sent_tokenize(text)
    ]


def isCandidateChunk(chunk):
    if not isinstance(chunk, nltk.Tree):
        return False

    if chunk.label() != "NP":
        return False

    for word, pos in chunk:
        if pos.startswith("NN"):
            return True

    return False

chunker = None

def getNounPhrases(html):
    global chunker
    if chunker is None:
        trainingChunkedSents = conll2000.chunked_sents("train.txt")#, chunk_types=['NP'])
        chunker = SimpleChunkParser(trainingChunkedSents)

    return [
        " ".join(word for word, pos in chunk)
        for sent in htmlSentTokenize(html)
        for chunk in chunker.parse(pos_tag(word_tokenize(sent)))
        if isCandidateChunk(chunk)
    ]

def getTagList(tags):
    """ Inputs string of "<tag><tag><tag>" and returns list [tag, tag, tag]"""
    tags = tags[1:len(tags)-1]
    return tags.split('><')

def sortByVal(user_val_list, isReverse=False):
    return sorted(user_val_list, key=lambda tup: tup[1], reverse=isReverse)    

def getNumOrderMismatches(user_vote_list, user_score_list):
    numMismatches = 0
    for i in range(len(user_score_list)):
        if user_vote_list[i][0] != user_score_list[i][0]:
            numMismatches += 1

    return numMismatches

def getListMismatchDistance(user_vote_list, user_score_list):
    mismatchDist = 0
    users_sorted_vote = [tup[0] for tup in user_vote_list]
    users_sorted_score = [tup[0] for tup in user_score_list]

    for i1, user_id in enumerate(users_sorted_vote):
        i2 = users_sorted_score.index(user_id)
        mismatchDist += abs(i1 - i2)

    return mismatchDist

def getRankLists(user_vote_list, user_score_list):
    users_sorted_vote = [tup[0] for tup in user_vote_list]
    users_sorted_score = [tup[0] for tup in user_score_list]

    vote_rank = []
    score_rank = []

    for i1, user_id in enumerate(users_sorted_vote):
        i2 = users_sorted_score.index(user_id)
        vote_rank.append(i1 + 1)
        score_rank.append(i2 + 1)

    return (vote_rank, score_rank)

def removeDuplicateUsers(user_vote_list):
    user_hash = {}
    tup_list = []
    for tup in user_vote_list:
        if tup[0] in user_hash:
            continue
        
        user_hash[tup[0]] = 1
        tup_list.append(tup)

    return tup_list
