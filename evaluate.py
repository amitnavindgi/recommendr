from model import Posts, Users
import pickle
import sys
import util

def main(test_set):
    """ test_set is a list of post ids """
    
    test_set_questions = Posts.select().where(Posts.id << test_set)
    for Post in test_set_questions:
        answers = Posts.select().where((Posts.posttypeid == 2) & (Posts.parentid == Post.id))
        #print answers.count()
        
        answer_details = []     # List of tuple (score, user_id)
        for answer in answers:
            if answer.owneruserid is not None:
                answer_details.append((answer.score, answer.owneruserid.id))
            else: 
                pass
                #print "None user object"
        
        answer_details = sorted(answer_details, key=lambda tup: tup[0], reverse=True)
        user_ids = [tup[1] for tup in answer_details]

        tags = util.getTagList(Post.tags)
        
        #TODO call feature generator
        #TODO Call predictor
        #TODO Do some computation using the results of predictor


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "/path/to/test_file_pickle")
    else:
        with open(sys.argv[1], 'r') as fin:
            test_set = pickle.load(fin)
        main(test_set)
