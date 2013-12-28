#-* coding: utf-8 -*-

from google.appengine.ext import ndb

import main_model_mixin as model_mixin

class ModelBase(ndb.Model):
  @classmethod
  def _post_get_hook(cls, key, future):
    entity = future.get_result()
    if entity is not None:
      entity.set_from_key()

  def set_from_key(self):
    pass

class User(ModelBase, model_mixin.User):
  #key
  #user_id = ndb.StringProperty(indexed=True, required=True)

  name = ndb.StringProperty(indexed=False)
  #not_do_today = list of Issue

class Project(ModelBase):
  #key auto

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
  datetime = ndb.DateTimeProperty(indexed=False, required=True)
  author = ndb.StringProperty(indexed=False, required=True)
  body = ndb.TextProperty(indexed=False, required=True)

class Issue(ModelBase, model_mixin.Issue):
  #key
  #project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
  #will_start_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  ##author_name = ndb.StringProperty(indexed=False)
  #author = ndb.KeyProperty(indexed=False, kind=User)

  subject = ndb.StringProperty(indexed=False, required=True)
  description = ndb.TextProperty(indexed=False)
  closed_on = ndb.DateTimeProperty(indexed=True)
  assignee = ndb.KeyProperty(indexed=True, kind=User)
  comment = ndb.LocalStructuredProperty(ArchivedComment, indexed=False, repeated=True, compressed=True)
  #closedしたらCommentを格納する

class WorkLoad(ModelBase, model_mixin.WorkLoad):
  #ユーザーは同時に複数のWorkLoadを作れない
  #key
  ##project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
  #issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  #start_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  #project_name = ndb.StringProperty(indexed=False, required=True)
  #issue_subject = ndb.StringProperty(indexed=False, required=True)

  end_at = ndb.DateTimeProperty(indexed=False)
  user = ndb.KeyProperty(indexed=True, kind=User, required=True)
  active = ndb.BooleanProperty(indexed=True, default=True)

class Comment(ModelBase, model_mixin.Comment):
  #key
  #issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  #time_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  #author_name = ndb.StringProperty(indexed=False, required=True)

  body = ndb.TextProperty(indexed=False, required=True)
  project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
