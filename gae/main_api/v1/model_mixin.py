#-* coding: utf-8 -*-

from datetime import datetime
import time

from google.appengine.ext import ndb
import tap
import tap.endpoints
import webapp2

class ModelMixinBase(object):
  @webapp2.cached_property
  def parsed_key(self):
    return self.__class__.parse_key(self.key)

class User(ModelMixinBase):
  @classmethod
  def gen_key(cls, user_id):
    return ndb.Key("User", user_id)

  @classmethod
  def parse_key(cls, key):
    return key.string_id()

  @property
  def user_id(self):
    return self.parsed_key

class Issue(ModelMixinBase):
  @classmethod
  def gen_key(cls, project_key, will_start_at, author_id, author_name):
    if not isinstance(will_start_at, str):
      will_start_at = tap.base62_encode(int(time.mktime(will_start_at.timetuple())))
    argv = (
      tap.base62_encode(project_key.integer_id()),
      will_start_at,
      author_id,
      author_name,
    )
    return ndb.Key("Issue", "/".join(argv))

  @classmethod
  def parse_key(cls, key):
    project_id, will_start_at, author_id, author_name = key.string_id().split("/", 3)
    result = (
      ndb.Key("Project", tap.base62_decode(project_id)),
      datetime.fromtimestamp(tap.base62_decode(will_start_at)),
      author_id,
      author_name,
    )
    return result

  @property
  def project_key(self):
    project_key, _will_start_at, _author_id, _author_name = self.parsed_key
    return project_key

  @property
  def will_start_at(self):
    _project_key, will_start_at, _author_id, _author_name = self.parsed_key
    return will_start_at

  @property
  def author_key(self):
    _project_key, _will_start_at, author_id, _author_name = self.parsed_key
    author_key = ndb.Key("User", author_id)
    return author_key

  @property
  def author_name(self):
    _project_key, _will_start_at, _author_id, author_name = self.parsed_key
    return author_name

class ActiveWorkLoad(ModelMixinBase):
  @classmethod
  @ndb.synctasklet
  def gen_key(cls, project_key, issue_key, start_at, user_key, user_name):
    project, issue = yield ndb.get_multi_async((project_key, issue_key))
    project_id, will_start_at, author_id, author_name = issue.key.string_id().split("/", 3)
    start_at = tap.base62_encode(int(time.mktime(start_at.timetuple())))
    project_name = project.name
    issue_subject = issue.subject
    user_id = user_key.string_id()
    argv = (
      user_id,
      project_id,
      will_start_at,
      author_id,
      author_name,
      start_at,
      project_name,
      issue_subject,
      user_name,
    )
    raise ndb.Return(ndb.Key("ActiveWorkLoad", "/".join(argv)))

  @classmethod
  def parse_key(cls, key):
    (
      user_id,
      project_id,
      will_start_at,
      author_id,
      author_name,
      start_at,
      project_name,
      issue_subject,
      user_name,
    ) = key.string_id().split("/", 8)

    project_key = ndb.Key("Project", tap.base62_decode(project_id))
    result = (
      project_key,
      Issue.gen_key(project_key, will_start_at, author_id, author_name), # issue_key
      datetime.fromtimestamp(tap.base62_decode(start_at)),  # start_at
      ndb.Key("User", user_id), # user_key
      user_name,
      project_name,
      issue_subject,
    )
    return result

  @property
  def project_key(self):
    (
      project_key,
      _issue_key,
      _start_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return project_key

  @property
  def issue_key(self):
    (
      _project_key,
      issue_key,
      _start_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return issue_key

  @property
  def start_at(self):
    (
      _project_key,
      _issue_key,
      start_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return start_at

  @property
  def user(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return user_key

  @property
  def user_name(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      _user_key,
      user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return user_name

  @property
  def project_name(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      _user_key,
      _user_name,
      project_name,
      _issue_subject,
    ) = self.parsed_key
    return project_name

  @property
  def issue_subject(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      _user_key,
      _user_name,
      _project_name,
      issue_subject,
    ) = self.parsed_key
    return issue_subject

  @property
  def user_name(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      _user_key,
      user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return user_name

class WorkLoad(ModelMixinBase):
  @classmethod
  @ndb.synctasklet
  def gen_key(cls, project_key, issue_key, start_at, end_at):
    project, issue = yield ndb.get_multi_async((project_key, issue_key))
    project_id, will_start_at, user_id, user_name = issue.key.string_id().split("/", 3)
    start_at = tap.base62_encode(int(time.mktime(start_at.timetuple())))
    end_at = tap.base62_encode(int(time.mktime(end_at.timetuple())))
    project_name = project.name
    issue_subject = issue.subject
    argv = (
      project_id,
      will_start_at,
      end_at,
      start_at,
      user_id,
      user_name,
      project_name,
      issue_subject,
    )
    raise ndb.Return(ndb.Key("WorkLoad", "/".join(argv)))

  @classmethod
  def parse_key(cls, key):
    (
      project_id,
      will_start_at,
      end_at,
      start_at,
      user_id,
      user_name,
      project_name,
      issue_subject,
    ) = key.string_id().split("/", 7)

    project_key = ndb.Key("Project", tap.base62_decode(project_id))
    result = (
      project_key,
      Issue.gen_key(project_key, will_start_at, user_id, user_name), # issue_key
      datetime.fromtimestamp(tap.base62_decode(start_at)),  # start_at
      datetime.fromtimestamp(tap.base62_decode(end_at)),  # end_at
      ndb.Key("User", user_id),
      user_name,
      project_name,
      issue_subject,
    )
    return result

  @property
  def project_key(self):
    (
      project_key,
      _issue_key,
      _start_at,
      _end_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return project_key

  @property
  def issue_key(self):
    (
      _project_key,
      issue_key,
      _start_at,
      _end_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return issue_key

  @property
  def start_at(self):
    (
      _project_key,
      _issue_key,
      start_at,
      _end_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return start_at

  @property
  def end_at(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      end_at,
      _user_key,
      _user_name,
      _project_name,
      _issue_subject,
    ) = self.parsed_key
    return end_at

  @property
  def project_name(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      _end_at,
      _user_key,
      _user_name,
      project_name,
      _issue_subject,
    ) = self.parsed_key
    return project_name

  @property
  def issue_subject(self):
    (
      _project_key,
      _issue_key,
      _start_at,
      _end_at,
      _user_key,
      _user_name,
      _project_name,
      issue_subject,
    ) = self.parsed_key
    return issue_subject

class Comment(ModelMixinBase):
  @classmethod
  @ndb.synctasklet
  def gen_key(cls, issue_key, time_at, author_key, author_name):
    project_id, will_start_at, user_id, name = issue_key.string_id().split("/", 3)
    argv = (
      project_id,
      will_start_at,
      user_id,
      name,
      tap.base62_encode(int(time.mktime(time_at.timetuple()))), #time_at
      author_key.string_id(), # author_id
      author_name,
    )
    raise ndb.Return(ndb.Key("Comment", "/".join(argv)))

  @classmethod
  def parse_key(cls, key):
    (
      project_id,
      will_start_at,
      user_id,
      name,
      time_at,
      author_id,
      author_name,
    ) = key.string_id().split("/", 6)

    project_key = ndb.Key("Project", tap.base62_decode(project_id))
    result = (
      Issue.gen_key(project_key, will_start_at, user_id, author_name), # issue_key
      datetime.fromtimestamp(tap.base62_decode(time_at)), # time_at
      ndb.Key("User", author_id), # author_key
      author_name,
    )
    return result

  @property
  def issue_key(self):
    (
      issue_key,
      _time_at,
      _author_key,
      _author_name,
    ) = self.__class__.parse_key(self.key)
    return issue_key

  @property
  def time_at(self):
    (
      _issue_key,
      time_at,
      _author_key,
      _author_name,
    ) = self.__class__.parse_key(self.key)
    return time_at

  @property
  def author_key(self):
    (
      _issue_key,
      _time_at,
      author_key,
      _author_name,
    ) = self.__class__.parse_key(self.key)
    return author_key

  @property
  def author_name(self):
    (
      _issue_key,
      _time_at,
      _author_key,
      author_name,
    ) = self.__class__.parse_key(self.key)
    return author_name

  @property
  def project_key(self):
    (
      issue_key,
      _time_at,
      _author_key,
      _author_name,
    ) = self.__class__.parse_key(self.key)
    project_key, _will_start_at, _user_key, _user_name = Issue.parse_key(issue_key)
    return project_key
