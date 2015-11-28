class FeatureGeneratorBase(object):
    """ Abstract Base class for Feature Generators """

    def learn(self):
        """ Learns the model for the feature generator """
        raise NotImplementedError()

    def getAnswerFeatures(self, answer):
        raise NotImplementedError()

    """ Abstract base class for a feature generation system """
    def getDocumentFeatures(self, document, tags):
        """ Returns a list of tuples (int, float) representing the feature vector for document """
        raise NotImplementedError()

    def getMaxDimSize(self):
        raise NotImplementedError()


class UserPredictorBase(object):
    """ Abstract Base class for User prediction system """

    def learn(self, fgen):
        """
        This method should implement learning for the model.

        fgen - a feature generator instance
        """
        raise NotImplementedError()

    def predictUsers(self, body, tags, fgen, n):
        """
        This method should implement learning for the model

        body - body of the question to be used for prediction
        tags - tags for the question to be used for prediction
        fgen - an instance of feature generator
        n    - number of user predictions to be made

        returns a list of n User objects
        """
        raise NotImplementedError()

    def predictUserScore(self, body, tags, fgen, users):
        """
        This method returns the ranking score for a user under the prediction
        algorithm

        body - body of the question to be used for prediction
        tags - tags for the question to be used for prediction
        fgen - an instance of feature generator
        users - list of user id for which the prediction should be generated

        returns a list of scores for corresponding users in users list
        """
        raise NotImplementedError()
