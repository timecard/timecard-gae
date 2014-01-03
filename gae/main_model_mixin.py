#-* coding: utf-8 -*-

from datetime import datetime
import time

from google.appengine.ext import ndb
import webapp2

class ModelMixinBase(object):
  @webapp2.cached_property
  def self_parse_key(self):
    return self.__class__.parse_key(self.key)

class User(ModelMixinBase):
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

class Issue(ModelMixinBase):
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

class WorkLoad(ModelMixinBase):
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

class Comment(ModelMixinBase):
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
    project_key, _will_start_at, _user = self.__class__.parse_key(issue_key)
    self.issue = issue_key
    self.author_name = author_name
    self.project = project_key
