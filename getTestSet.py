from model import Posts
import pickle
import random
import sys

if __name__ == "__main__":
    test_size = 1000
    answers = Posts.select().where((Posts.posttypeid == 1) & (Posts.answercount >= 2))
    ids = []
    for Post in answers:
        ids.append(Post.id)

    random.shuffle(ids)
    ids = question_ids[:test_size]
    for id in ids:
        print("Setting forevaluation for question {0}".format(id))
        q = Posts.update(forevaluation = 1).where(Posts.id == id)
        q.execute()
