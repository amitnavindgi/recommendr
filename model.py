from peewee import *
import config

database = SqliteDatabase(config.DATABASE_FILENAME, **{})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Users(BaseModel):
    aboutme = TextField(db_column='AboutMe', null=True)
    accountid = IntegerField(db_column='AccountId', null=True)
    age = IntegerField(db_column='Age', null=True)
    creationdate = DateTimeField(db_column='CreationDate', null=True)
    displayname = TextField(db_column='DisplayName', null=True)
    downvotes = IntegerField(db_column='DownVotes', null=True)
    emailhash = TextField(db_column='EmailHash', null=True)
    id = PrimaryKeyField(db_column='Id', null=True)
    lastaccessdate = DateTimeField(db_column='LastAccessDate', null=True)
    location = TextField(db_column='Location', null=True)
    profileimageurl = TextField(db_column='ProfileImageUrl', null=True)
    reputation = IntegerField(db_column='Reputation', null=True)
    upvotes = IntegerField(db_column='UpVotes', null=True)
    views = IntegerField(db_column='Views', null=True)
    websiteurl = TextField(db_column='WebsiteUrl', null=True)

    class Meta:
        db_table = 'Users'

class Badges(BaseModel):
    date = DateTimeField(db_column='Date', null=True)
    id = PrimaryKeyField(db_column='Id', null=True)
    name = TextField(db_column='Name', null=True)
    userid = ForeignKeyField(db_column='UserId', null=True, rel_model=Users, to_field='id')

    class Meta:
        db_table = 'Badges'

class Posts(BaseModel):
    acceptedanswerid = IntegerField(db_column='AcceptedAnswerId', null=True)
    answercount = IntegerField(db_column='AnswerCount', null=True)
    body = TextField(db_column='Body', null=True)
    closeddate = DateTimeField(db_column='ClosedDate', null=True)
    commentcount = IntegerField(db_column='CommentCount', null=True)
    communityowneddate = DateTimeField(db_column='CommunityOwnedDate', null=True)
    creationdate = DateTimeField(db_column='CreationDate', null=True)
    favoritecount = IntegerField(db_column='FavoriteCount', null=True)
    forevaluation = IntegerField(db_column='ForEvaluation', null=True)
    id = PrimaryKeyField(db_column='Id', null=True)
    lastactivitydate = DateTimeField(db_column='LastActivityDate', null=True)
    lasteditdate = DateTimeField(db_column='LastEditDate', null=True)
    lasteditordisplayname = TextField(db_column='LastEditorDisplayName', null=True)
    lasteditoruserid = ForeignKeyField(db_column='LastEditorUserId', null=True, rel_model=Users, to_field='id')
    ownerdisplayname = TextField(db_column='OwnerDisplayName', null=True)
    owneruserid = ForeignKeyField(db_column='OwnerUserId', null=True, rel_model=Users, related_name='Users_owneruserid_set', to_field='id')
    parentid = ForeignKeyField(db_column='ParentID', null=True, rel_model='self', to_field='id')
    posttypeid = IntegerField(db_column='PostTypeId', null=True)
    score = IntegerField(db_column='Score', null=True)
    tags = TextField(db_column='Tags', null=True)
    title = TextField(db_column='Title', null=True)
    viewcount = IntegerField(db_column='ViewCount', null=True)
    forevaluation = IntegerField(db_column='ForEvaluation', null=True)

    class Meta:
        db_table = 'Posts'

class Comments(BaseModel):
    creationdate = DateTimeField(db_column='CreationDate', null=True)
    id = PrimaryKeyField(db_column='Id', null=True)
    postid = ForeignKeyField(db_column='PostId', null=True, rel_model=Posts, to_field='id')
    score = IntegerField(db_column='Score', null=True)
    text = TextField(db_column='Text', null=True)
    userdisplayname = TextField(db_column='UserDisplayName', null=True)
    userid = ForeignKeyField(db_column='UserId', null=True, rel_model=Users, to_field='id')

    class Meta:
        db_table = 'Comments'

class Tags(BaseModel):
    id = PrimaryKeyField(db_column='Id', null=True)
    tag = TextField(db_column='Tag', null=True)

    class Meta:
        db_table = 'Tags'

class Tagpostmap(BaseModel):
    id = PrimaryKeyField(db_column='Id', null=True)
    postid = ForeignKeyField(db_column='PostId', null=True, rel_model=Posts, to_field='id')
    tagid = ForeignKeyField(db_column='TagId', null=True, rel_model=Tags, to_field='id')

    class Meta:
        db_table = 'TagPostMap'

class Votes(BaseModel):
    bountyamount = IntegerField(db_column='BountyAmount', null=True)
    creationdate = DateTimeField(db_column='CreationDate', null=True)
    id = PrimaryKeyField(db_column='Id', null=True)
    postid = ForeignKeyField(db_column='PostId', null=True, rel_model=Posts, to_field='id')
    userid = ForeignKeyField(db_column='UserId', null=True, rel_model=Users, to_field='id')
    votetypeid = IntegerField(db_column='VoteTypeId', null=True)

    class Meta:
        db_table = 'Votes'

class SqliteSequence(BaseModel):
    name = UnknownField()  # 
    seq = UnknownField()  # 

    class Meta:
        db_table = 'sqlite_sequence'

