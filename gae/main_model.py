#-* coding: utf-8 -*-
from google.appengine.ext import ndb

class User(ndb.Model):
  #key = user.user_id()
  name = ndb.StringProperty(indexed=False)
  #not_do_today = list of Issue

class Project(ndb.Model):
  name = ndb.StringProperty(indexed=False, required=True)
  description = ndb.TextProperty(indexed=False)
  is_public = ndb.BooleanProperty(indexed=False, default=True)
  closed = ndb.BooleanProperty(indexed=False, default=False)
  archive = ndb.BooleanProperty(indexed=False, default=False)
  admin = ndb.KeyProperty(indexed=True, kind=User, repeated=True) #required=True
  member = ndb.KeyProperty(indexed=False, kind=User, repeated=True)
  #github
  #ruffnote

class ArchivedComment(ndb.Model):
  body = ndb.TextProperty(indexed=False, required=True)
  author = ndb.StringProperty(indexed=False, required=True)
  datetime = ndb.DateTimeProperty(indexed=False, required=True)

class Issue(ndb.Model):
  subject = ndb.StringProperty(indexed=False, required=True)
  description = ndb.TextProperty(indexed=False)
  will_start_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  closed_on = ndb.DateTimeProperty(indexed=True)
  project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
  author = ndb.StringProperty(indexed=False)
  assignee = ndb.KeyProperty(indexed=True, kind=User)
  comment = ndb.LocalStructuredProperty(ArchivedComment, indexed=False, repeated=True, compressed=True)
  #closedしたらCommentを格納する

class WorkLoad(ndb.Model):
  #ユーザーは同時に複数のWorkLoadを作れない
  start_at = ndb.DateTimeProperty(indexed=False, required=True)
  end_at = ndb.DateTimeProperty(indexed=False)
  issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  user = ndb.KeyProperty(indexed=True, kind=User, required=True)
  active = ndb.BooleanProperty(indexed=True, default=True)
  project = ndb.KeyProperty(indexed=True, kind=Project, required=True)

class Comment(ndb.Model):
  body = ndb.TextProperty(indexed=False, required=True)
  issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  author = ndb.StringProperty(indexed=False, required=True)
  datetime = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
