import pickle
from project544.base import UserPredictorBase
from project544 import config
from project544.model import Users
from gensim import similarities
from project544.topicmodelling.tm import TopicModel

class TopicModelPredictor(UserPredictorBase):
    def __init__(self, indexfile=config.USER_INDEX):
        self.index = similarities.MatrixSimilarity.load(indexfile)

    def predictUsers(self, body, tags, fgen, n=3):
        featureVector = fgen.getDocumentFeatures(body)

        try:
            sims = self.index[featureVector]
        except Exception:
            return None

        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        with open(config.USERS_LIST, 'r') as inpfile:
            userlist = pickle.load(inpfile)
        userIds = [userlist[sim[0]] for sim in sims[:n]]
        return Users.select().where(Users.id << userIds)

    def predictUserScore(self, body, tags, fgen, users):
        featureVector = fgen.getDocumentFeatures(body)

        try:
            sims = self.index[featureVector]
        except Exception:
            return None

        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        with open(config.USERS_LIST, 'r') as inpfile:
            userlist = pickle.load(inpfile)
            scores = [sim[1] for sim in sims if userlist[sim[0]] in users]
        return scores

if __name__ == '__main__':
    predictor = TopicModelPredictor()
    fgen      = TopicModel()
    question  = '''What is the following variation on Set Cover known as?'''

    users = predictor.predictUsers(question, None, fgen, 5)
    for user in users:
        print user.displayname

    userlist  = [3186, 11447, 8441, 1693]
    scores = predictor.predictUserScore(question, None, fgen, userlist)
    print scores
