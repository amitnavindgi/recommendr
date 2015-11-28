from base import FeatureGeneratorBase
from topicmodelling.tm import TopicModel
from tag_feature_gen import TagFeatureGen

class TagTMFeatureGen(FeatureGeneratorBase):
    def __init__(self):
        self.tm = TopicModel()
        self.tg = TagFeatureGen()

    def getAnswerFeatures(self, answer):
        #print("Combining features for answer {0}".format(answer.id))
        tmFeatures = self.tm.getAnswerFeatures(answer)
        tgFeatures = [(key+10+self.tm.getMaxDimSize(), value) for key, value in self.tg.getAnswerFeatures(answer)]
        return tmFeatures + tgFeatures

    def getDocumentFeatures(self, document, tags):
       # print("Combining features for document")
        tmFeatures = self.tm.getDocumentFeatures(document, tags)
        tgFeatures = [(key+10+self.tm.getMaxDimSize(), value) for key, value in self.tg.getDocumentFeatures(document, tags)]
        return tmFeatures + tgFeatures

    def getMaxDimSize(self):
        return (self.tm.getMaxDimSize() + self.tg.getMaxDimSize())

