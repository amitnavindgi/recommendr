import os
from tm import TopicModel
import config
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class TopicModelViz:

    def __init__(self, modelfile=config.CURRENT_MODEL):
        self.topicmodel = TopicModel()

        self.terms = []
        for i in range(config.NUM_TOPICS_LDA):
            temp = self.topicmodel.model.show_topic(i, 80)
            terms = []
            for term in temp:
                terms.append(term)
            self.terms.append(terms)

    def terms_to_wordcounts(self, terms, multiplier=1000):
        return " ".join([" ".join(int(multiplier*i[0]) * [i[1]]) for i in terms])

    def genWordCloud(self, index, font_path = None):
        wordcloud = WordCloud(background_color="white", font_path=font_path).generate(self.terms_to_wordcounts(self.terms[index]))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig(os.path.join(config.VISUALIZATION_FOLDER,"wordcloud_"+str(index)))
        plt.close()

    def genWordClouds(self, font_path = None):
        for i in range(config.NUM_TOPICS_LDA):
            self.genWordCloud(i, font_path = font_path)

    def genTopicProportion(self, question):
        topic_prop = self.topicmodel.getDocumentFeatures(question)
        plt.scatter(*zip(*topic_prop))
        plt.savefig(os.path.join(config.VISUALIZATION_FOLDER,"doc_scatterplot"))
        plt.close()

    def genUserTopicProportion(self, userid):
        topic_prop = self.topicmodel.getUserFeatures(userid)
        plt.scatter(*zip(*topic_prop))
        plt.savefig(os.path.join(config.VISUALIZATION_FOLDER,"user" + str(userid) + "_scatterplot"))
        plt.close()

if __name__ == "__main__":
    import sys
    font_path = None
    if len(sys.argv) == 2:
        font_path = sys.argv[1]
    topicmodelviz = TopicModelViz()
    topicmodelviz.genWordClouds(font_path = font_path)
