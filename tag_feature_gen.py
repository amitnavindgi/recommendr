from peewee import fn

from base import FeatureGeneratorBase
from model import Posts, Tags, database

class TagFeatureGen(FeatureGeneratorBase):
    def __init__(self):
        self.maxDimSize = None

    def getAnswerFeatures(self, answer):
        sql = """
            select tagCounts.TagId,
                   (CAST(tagCounts.counts AS FLOAT)/(select count(*) from TagPostMap as tagPm where tagPm.TagId=tagCounts.TagId))
            from
                    Posts as answerOuter
            join Posts as questionOuter
                    on questionOuter.Id = answerOuter.ParentID
            join TagPostMap as tagpm
                    on tagpm.PostId = questionOuter.Id
            join
            (
                    select tagpm.TagId, ClassifierUserPredictorcount(tagpm.TagId) as counts from Posts as answer
                    join Posts as question
                            on answer.ParentID = question.Id
                    join TagPostMap as tagpm
                            on tagpm.PostId = question.Id
                    where
                            answer.PostTypeId = 2 and answer.OwnerUserId=?
                    group by tagpm.TagId
            ) as tagCounts
            on tagCounts.TagId = tagpm.TagId
            join Tags as tag
                    on tag.Id = tagCounts.TagId
            where answerOuter.Id = ?
        """
        return list(database.execute_sql(sql, (answer.owneruserid.id, answer.id)))

    def getTagIds(self, tags):
        print(tags)
        tagIds = []
        for tagStr in tags:
            tag = Tags.get(Tags.tag == tagStr)
            if tag is not None:
                tagIds.append(tag.id)
        return tagIds

    def getDocumentFeatures(self, document, tags):
        return [(tagId, 1) for tagId in self.getTagIds(tags)]

    def getMaxDimSize(self):
        if self.maxDimSize is None:
            self.maxDimSize = Tags.select(fn.count(Tags.id)).scalar()
        return self.maxDimSize
