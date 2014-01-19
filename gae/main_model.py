# -* coding: utf-8 -*-

from google.appengine.ext import ndb

import main_model_mixin as model_mixin

LANGUAGE_CHOICES = (
  ("en", u"English"),
  ("ja", u"日本語"),
)

class User(ndb.Model, model_mixin.User):
  #key
  #user_id = ndb.StringProperty(indexed=True, required=True)

  name = ndb.StringProperty(indexed=False)
  language = ndb.StringProperty(indexed=False, choices=[value for value, label in LANGUAGE_CHOICES], default=LANGUAGE_CHOICES[0][0])
  #not_do_today = list of Issue

class Project(ndb.Model):
  #key auto

  name = ndb.StringProperty(indexed=False, required=True)
  description = ndb.TextProperty(indexed=False, default="")
  is_public = ndb.BooleanProperty(indexed=True, default=True)
  closed = ndb.BooleanProperty(indexed=False, default=False)
  archive = ndb.BooleanProperty(indexed=False, default=False)
  admin = ndb.KeyProperty(indexed=True, kind=User, repeated=True) #required=True
  member = ndb.KeyProperty(indexed=True, kind=User, repeated=True)
  #github
  #ruffnote

  def _pre_put_hook(self):
    assert len(self.admin) > 0
    assert len(self.member) > 0
    assert set(self.admin).issubset(set(self.member))

class ArchivedComment(ndb.Model):
  datetime = ndb.DateTimeProperty(indexed=False, required=True)
  author = ndb.StringProperty(indexed=False, required=True)
  body = ndb.TextProperty(indexed=False, required=True)

class Issue(ndb.Model, model_mixin.Issue):
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

class ActiveWorkLoad(ndb.Model, model_mixin.ActiveWorkLoad):
  #ユーザーは同時に複数のWorkLoadを作れない
  #key
  #user = ndb.KeyProperty(indexed=True, kind=User, required=True)
  ##project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
  #issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  #start_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  #project_name = ndb.StringProperty(indexed=False, required=True)
  #issue_subject = ndb.StringProperty(indexed=False, required=True)
  pass

class WorkLoad(ndb.Model, model_mixin.WorkLoad):
  #key
  ##project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
  #issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  #start_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  #project_name = ndb.StringProperty(indexed=False, required=True)
  #issue_subject = ndb.StringProperty(indexed=False, required=True)
  #end_at = ndb.DateTimeProperty(indexed=False)
  #user = ndb.KeyProperty(indexed=True, kind=User, required=True)

  user = ndb.KeyProperty(indexed=True, kind=User, required=True)

class Comment(ndb.Model, model_mixin.Comment):
  #key
  ##project = ndb.KeyProperty(indexed=True, kind=Project, required=True)
  #issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  #time_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  #author_id = ndb.StringProperty(indexed=False, required=True)
  #author_name = ndb.StringProperty(indexed=False, required=True)

  body = ndb.TextProperty(indexed=False, required=True)
  update_at = ndb.DateTimeProperty(indexed=False)
