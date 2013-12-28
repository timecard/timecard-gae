#-* coding: utf-8 -*-

from datetime import datetime
import time

from google.appengine.ext import ndb
import webapp2

class ModelBase(ndb.Model):
  @classmethod
  def _post_get_hook(cls, key, future):
    entity = future.get_result()
    if entity is not None:
      entity.set_from_key()

  def set_from_key(self):
    pass

  @webapp2.cached_property
  def self_parse_key(self):
    return self.__class__.parse_key(self.key)

class User(ModelBase):
  #key
  #user_id = ndb.StringProperty(indexed=True, required=True)

  name = ndb.StringProperty(indexed=False)
  #not_do_today = list of Issue

  @classmethod
  def gen_key(cls, user):
    argv = tuple(
      user.user_id(),
    )
    return ndb.Key(cls, ":".join(argv))

  @classmethod
  def parse_key(cls, key):
    return key.string_id()

  def set_from_key(self):
    self.user_id = self.key.string_id()

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

class Issue(ModelBase):
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

  @classmethod
  def gen_key(cls, project_key, will_start_at, author):
    if not isinstance(will_start_at, str):
      will_start_at = str(int(time.mktime(will_start_at.timetuple())))
    argv = tuple(
      project.key.string_id(),
      will_start_at,
      author.user_id,
      author.name,
    )
    return ndb.Key(cls, "/".join(argv))

  @classmethod
  def parse_key(cls, key):
    project_id, will_start_at, user_id, name = key.string_id().split("/", 3)
    result = tuple(
      project_key = ndb.Key(Project, project_id),
      will_start_at = datetime.fromtimestamp(int(will_start_at)),
      user = User(ndb.Key(User, user_id), name=name),
    )
    return result

  def set_from_key(self):
    project_key, will_start_at, user = self.__class__.parse_key(self.key)
    self.project = project_key
    self.will_start_at = will_start_at
    self.author = user

class WorkLoad(ModelBase):
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

  @classmethod
  @ndb.synctasklet
  def gen_key(cls, project_key, issue_key, start_at):
    project, issue = yield ndb.get_multi_async((project_key, issue_key))
    project_id, will_start_at, user_id, name = key.string_id().split("/", 3)
    start_at = str(int(time.mktime(datetime.now().timetuple()))),
    project_name = project.name
    issue_subject = issue.subject
    argv = tuple(
      project_id,
      will_start_at,
      user_id,
      name,
      start_at,
      project_name,
      issue_subject,
    )
    raise ndb.Return(ndb.Key(cls, "/".join(argv)))

  @classmethod
  def parse_key(cls, key):
    (
      project_id,
      will_start_at,
      user_id,
      name,
      start_at,
      project_name,
      issue_subject,
    ) = key.string_id().split("/", 6)

    project_key = ndb.Key(Project, project_id),
    author = User(ndb.Key(User, user_id), name=name)
    result = tuple(
      project_key,
      Issue.gen_key(project_key, will_start_at, author), # issue_key
      datetime.fromtimestamp(int(start_at)),  # start_at
      project_name,
      issue_subject,
    )
    return result

  def set_from_key(self):
    (
      project_key,
      issue_key,
      start_at,
      project_name,
      issue_subject,
    ) = self.__class__.parse_key(self.key)
    self.project = project_key
    self.issue = issue_key
    self.start_at = start_at
    self.project_name = project_name
    self.issue_subject = issue_subject

class Comment(ModelBase):
  #key
  #issue = ndb.KeyProperty(indexed=True, kind=Issue, required=True)
  #time_at = ndb.DateTimeProperty(indexed=False, auto_now_add=True)
  #author_name = ndb.StringProperty(indexed=False, required=True)

  body = ndb.TextProperty(indexed=False, required=True)
  project = ndb.KeyProperty(indexed=True, kind=Project, required=True)

  @classmethod
  @ndb.synctasklet
  def gen_key(cls, issue_key, author_name):
    project_id, will_start_at, user_id, name = issue_key.string_id().split("/", 3)
    argv = tuple(
      project_id,
      will_start_at,
      user_id,
      name,
      str(int(time.mktime(datetime.now().timetuple()))), #time_at
      author_name,
    )
    raise ndb.Return(ndb.Key(cls, "/".join(argv)))

  @classmethod
  def parse_key(cls, key):
    (
      project_id,
      will_start_at,
      user_id,
      name,
      time_at,
      author_name,
    ) = key.string_id().split("/", 5)

    project_key = ndb.Key(Project, project_id),
    author = User(ndb.Key(User, user_id), name=name)
    result = tuple(
      Issue.gen_key(project_key, will_start_at, author), # issue_key
      author_name,
    )
    return result

  def set_from_key(self):
    (
      issue_key,
      author_name,
    ) = self.__class__.parse_key(self.key)
    self.issue = issue_key
    self.author_name = author_name
