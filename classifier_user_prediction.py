from sklearn.linear_model import Perceptron
from sklearn.feature_extraction import FeatureHasher
import numpy
import pickle
import peewee
import scipy
import math
import config
import util
from base import UserPredictorBase
from model import Posts, Users, Tags, Tagpostmap

class ClassifierUserPredictor(UserPredictorBase):
    def __init__(self, classifier=None, batchSize=1000):
        if classifier is None:
            classifier = Perceptron()
        self.cf = classifier
        self.batchSize = 1000

    def learn(self, fgen, postLimit=None):
        Parent = Posts.alias()
        query = Posts.select().join(Parent, on=(Posts.parentid == Parent.id)).where(Posts.posttypeid == 2 & Parent.forevaluation == 0)
        if postLimit is not None:
            query = query.limit(postLimit)
        count = query.count()
        print("Learning {0} questions".format(count))

        allClasses = numpy.array([user.id for user in Users.select()])

        maxUserRep = float(Users.select(peewee.fn.Max(Users.reputation)).scalar())

        featureHasher = FeatureHasher(n_features = fgen.getMaxDimSize()+4, input_type = 'pair')
        featureMatrix = []
        classList = []
        for i, answer in enumerate(query):
            if answer.owneruserid is None:
                continue
            print("Generating feature vector for id {0}".format(answer.id))
            # docment features
            #featureVector = fgen.getDocumentFeatures(answer.parentid.title + answer.parentid.body + answer.body, tagIds)
            #featureVector = fgen.getAnswerFeatures(answer)
            featureVector = []
            #eatureVector = [(str(dim), value) for dim, value in featureVector]
            # additional features
            maxScore = Posts.select(peewee.fn.Max(Posts.score)).where(Posts.parentid == answer.parentid).scalar()
            maxLength = max(len(post.body) for post in Posts.select().where(Posts.parentid == answer.parentid))
            featureVector.append(("L                                                                                                                                                                                                                                                                                                                                            ength", (len(answer.body)/float(maxLength))))
            featureVector.append(("Score", 1 if maxScore == 0 else (answer.score/float(maxScore))))
            featureVector.append(("Accepted", 1 if answer.id == answer.parentid.acceptedanswerid else 0))
            featureVector.append(("OwnerRep", answer.owneruserid.reputation/maxUserRep))

            featureMatrix.append(featureVector)
            classList.append(answer.owneruserid.id)
            if len(featureMatrix) == self.batchSize or i == count-1:
                print("Partial fitting classifier".format(answer.id))
                X = featureHasher.transform(featureMatrix)
                Y = numpy.array(classList)
                self.cf.partial_fit(X, Y, classes=allClasses)
                allClasses = None
                featureMatrix = []
                classList = []


    def predictUsers(self, body, tags, fgen, n = 3):
        featureHasher = FeatureHasher(n_features = fgen.getMaxDimSize()+4, input_type = 'pair')
        # document features
        featureVector = [(str(dim), value) for dim, value in fgen.getDocumentFeatures(body, tags)]
        # additional features
        featureVector.append(("Length", 1))
        featureVector.append(("Score", 1))
        featureVector.append(("Accepted", 1))
        featureVector.append(("OwnerRep", 1))

        X = featureHasher.transform([[(str(dim), value) for dim, value in featureVector]])
        userIds = [int(self.cf.classes_[index]) for index, score in sorted(enumerate(self.cf.decision_function(X)[0]), key=lambda x:x[1], reverse=True)][:n]
        # print(userIds)
        # print(self.cf.predict(X))

        return [Users.get(Users.id == userId) for userId in userIds]

    def predictUserScore(self, body, tags, fgen, users):
        featureHasher = FeatureHasher(n_features = fgen.getMaxDimSize()+4, input_type = 'pair')
        # document features
        featureVector = [(str(dim), value) for dim, value in fgen.getDocumentFeatures(body, tags)]
        # additional features
        featureVector.append(("Length", 1))
        featureVector.append(("Score", 1))
        featureVector.append(("Accepted", 1))
        featureVector.append(("OwnerRep", 1))

        X = featureHasher.transform([[(str(dim), value) for dim, value in featureVector]])
        scores = [score for index, score in enumerate(self.cf.decision_function(X)[0]) if int(self.cf.classes_[index]) in users]
        return scores

def testLearn():
    # from project544.topicmodelling.tm import TopicModel
    # tm = TopicModel()
    # up = ClassifierUserPredictor()
    # up.learn(tm)
    # file = open(config.USER_PREDICTOR_TM, "w")
    # pickle.dump(up, file)
    # file.close()

    # from project544.tag_feature_gen import TagFeatureGen
    # tg = TagFeatureGen()
    # up = ClassifierUserPredictor()
    # up.learn(tg)
    # file = open(config.USER_PREDICTOR_TG, "w")
    # pickle.dump(up, file)
    # file.close()

    from project544.tag_feature_gen import TagFeatureGen
    tg = TagFeatureGen()
    up = ClassifierUserPredictor()
    up.learn(tg)
    file = open(config.USER_PREDICTOR_TG, "w")
    pickle.dump(up, file)
    file.close()

def findNDCG(rel):
    dcg = 0
    for i, r in enumerate(rel):
       dcg += (math.pow(2, r)-1)/math.log(i+1, 2)

    idcg = 0
    for i, r in enumerate(sorted(rel, reverse=True)):
       idcg += (math.pow(2, r)-1)/math.log(i+1, 2)

    return dcg/idcg

def testPredictEval(up, tgen, kSet):
    query = Posts.select().where((Posts.posttypeid == 1) & (Posts.forevaluation == 1) & (Posts.answercount >= 2))
    query = query[0:9]
    pak = dict((k,0) for k in kSet)
    mrr = 0
    for question in query:
        tags = util.getTagList(question.tags)
        predictions = [user.id for user in up.predictUsers(question.body, tags, tgen, n = max(kSet))]
        answers = Posts.select().where((Posts.posttypeid == 2) & (Posts.parentid == question.id))
        answerUserIds = [ans.owneruserid.id  for ans in answers if ans.owneruserid is not None and ans.score > 0]


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

def plot(results, kSets, colors, order=None):
    import numpy as np
    import matplotlib.pyplot as plt

    if order is None:
        print(results.keys())
        order = results.keys()

    ind = np.arange(len(kSets))
    indMrr = np.arange(len(results))
    barWidth = 0.20

    figPak, axPak = plt.subplots()
    figMrr, axMrr = plt.subplots()

    axPak.set_xticks(ind + (barWidth*len(results)/float(2)))
    axPak.set_xticklabels(["k={0}".format(k) for k in kSets])

    axMrr.set_xticks(indMrr)
    axMrr.set_xticklabels(order)
    # figMrr, axMrr = plt.subplots()
    rectsPak = {}
    # rectsMrr = {}
    for i, name in enumerate(order):
        pak, mrr = results[name]
        temp = []
        for k in kSets:
            for j in pak:
                if j[0] == k:
                    print(j)
                    print(j[0])
                    print(j[1])
                    temp.append(j[1])
        print(temp)
        rectsPak[name] = axPak.bar(ind + i*barWidth, temp, barWidth, color=colors[i])

    axMrr.bar(indMrr, [results[name][1] for name in order], barWidth, align="center", color=colors[1])
    plt.xlim([min(indMrr)-0.5, max(indMrr)+0.5])
    # for i, (name, (pak, mrr)) in enumerate(results.items()):
    #     rectsPak[name] = axPak.bar(ind + i*barWidth, [pak[k] for k in kSets], barWidth, color=colors[i])

    legendLabels = order
    axPak.legend( [rectsPak[label] for label in legendLabels], legendLabels )
    plt.show()


def evaluate():
    from project544.topicmodelling.tm import TopicModel
    from project544.tag_feature_gen import TagFeatureGen
    from project544.tag_tm_feature_gen import TagTMFeatureGen
    tgen = TagTMFeatureGen()
    tgen = TopicModel()
    tgen = TagFeatureGen()
    methods = {
 #       "Topic Modelling": (config.USER_PREDICTOR_TM, TopicModel),
        "Post Tags": (config.USER_PREDICTOR_TG, TagFeatureGen),
        "Combined": (config.USER_PREDICTOR_TGTM, TagTMFeatureGen)
    }
    kSet = (1, 10, 50,100,1000)
    results = {}
    for name, (upFilename, tgenClass) in methods.items():
        print("Evaluating {0} with kSet={1}".format(name, repr(kSet)))
        file = open(upFilename, "r")
        up = pickle.load(file)
        file.close()
        tgen = tgenClass()
        results[name] = testPredictEval(up, tgen, kSet)
    plot(results, kSet, ( "#CC405D", "#F2BB77"))


def testPredict():
    from project544.util import stripTags

    file = open(config.USER_PREDICTOR_TG, "r")
    up = pickle.load(file)
    file.close()

    with open(config.TEST_SET, 'r') as fin:
        test_set = pickle.load(fin)

    from project544.topicmodelling.tm import TopicModel
    from project544.tag_feature_gen import TagFeatureGen
    tm = TopicModel()
    # tm = TagFeatureGen()

    #query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 7000)).limit(5)
    total_num_mismatches = 0
    total_mismatch_dist = 0
    total_score = 0
    total_users_predicted = 0
    total_spearman_coeff = 0
    total_nan_count  = 0

    query = Posts.select().where(Posts.id << test_set)
    for question in query:
        print("*"*80)
        tags = util.getTagList(question.tags)
        users = up.predictUsers(question.body, tags, tm, n = 10)
        answers = Posts.select().where((Posts.posttypeid == 2) & (Posts.parentid == question.id))

        user_vote_list = []     # List of tuple (score, user_id)
        for answer in answers:
            if answer.owneruserid is not None:
                user_vote_list.append((answer.owneruserid.id, answer.score))
            else:
                pass
                #print "None user object"

        user_vote_list = util.removeDuplicateUsers(util.sortByVal(user_vote_list, True))
        user_ids = [tup[0] for tup in user_vote_list]

        scores = up.predictUserScore(question.body, tags, tm, user_ids)
        if (len(user_vote_list) != len(scores)):
            print("ERROR")
            print(question.id)
            print(user_vote_list)
            print(scores)

        user_score_list = [(user_vote_list[i][0], scores[i]) for i in range(len(user_vote_list))]
        user_score_list = util.sortByVal(user_score_list)

        num_mismatches = util.getNumOrderMismatches(user_vote_list, user_score_list)
        mismatch_dist = util.getListMismatchDistance(user_vote_list, user_score_list)

        total_num_mismatches += num_mismatches
        total_mismatch_dist += mismatch_dist

        #vote_vals = [tup[1] for tup in user_vote_list]
        #score_vals = [(-1 * scores[i]) for i in range(len(user_vote_list))]

        vote_vals, score_vals = util.getRankLists(user_vote_list, user_score_list)

        spearman_val = scipy.stats.spearmanr(vote_vals, score_vals)
        if math.isnan(spearman_val[0]):
            #print("NAN!!!")
            #print vote_vals
            #print score_vals
            total_nan_count += 1
        else:
            total_spearman_coeff += spearman_val[0]

        print("Top predictions for Post {0}".format(question.id))
        print("-------------------------")
        print(stripTags(question.title).encode('utf-8'))
        print("")
        print(stripTags(question.body).encode('utf-8'))
        print("-------------------------")
        print([user.displayname for user in users])
        print("")

        print("User Scores for Post {0}".format(question.id))
        print("user_id" + "\t" + "votes" + "\t" + "prediction score")
        for index, tup in enumerate(user_vote_list):
            print str(tup[0]) + '\t' + str(tup[1]) + '\t' + str(scores[index])
            total_score += scores[index]
            total_users_predicted += 1

        print("")
        print([tup[0] for tup in user_vote_list])
        print([tup[0] for tup in user_score_list])
        print("")
        print("Num Mismatches: {0}".format(num_mismatches))
        print("Mismatch Dist (Total): {0}".format(mismatch_dist))
        print("Spearman Coeff: {0}".format(spearman_val[0]))
        print("")
        print("*"*80)

    if total_users_predicted > 0:
        total_questions = query.count()
        print("")
        print("Aggregated Statistics:")
        print("Average Num Mismatches: {0}".format(total_num_mismatches / total_questions))
        print("Average mismatch dist per question: {0}".format(total_mismatch_dist / total_questions))
        print("Average mismatch dist per user: {0}".format(total_mismatch_dist / total_users_predicted))
        print("Average Spearman coeff: {0}".format(total_spearman_coeff / (total_questions - total_nan_count)))
        print("Average score: {0}".format(total_score / total_users_predicted))
    #query = Posts.select().where((Posts.posttypeid == 1) & (Posts.id > 6000)).limit(5)
    #for question in query:
    #    users = [answer.owneruserid for answer in Posts.select().where(Posts.parentid == question.id)]
    #    userIds = [user.id for user in users]
    #    scores = up.predictUserScore(question.body, None, tm, userIds)
    #    print("User Scores for Post {0}".format(question.id))
    #    print("\n".join("{0}({1})".format(user.displayname, score) for user, score in zip(users, scores)))
    #    print("")
RESULTS = {
    "Tag Generator": (
	dict([(1, 0.188), (10, 0.045), (20, 0.02525), (5, 0.0786), (100, 0.00603)]),
	0.26780247855
    ),
    "TM Generator": (
	dict([(1, 0.084), (10, 0.0278), (20, 0.01665), (5, 0.0472), (100, 0.00388)]),
	0.144174681867
    ),
    "Combined": (
	dict([(1, 0.186), (10, 0.0492), (20, 0.0266), (5, 0.0856), (100, 0.00653)]),
	0.276254813686
    )
}
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Invalid arguments")
    else:
        if sys.argv[1] == "learn":
            testLearn()
        else:
            # testPredictEval()
            evaluate()

