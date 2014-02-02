from datetime import datetime

import logging
import tap

from google.appengine.ext import ndb
import webapp2

from main_api.v1 import api
from main_api.v1 import user as api_user
from main_api.v1 import model

angular = "js.angular.angular"
bootstrap = "js.bootstrap.bootstrap"

class BaseHandler(tap.RequestHandler):
  i18n = True
  i18n_domain = "timecard"
  language_list = model.LANGUAGE_CHOICES

  @webapp2.cached_property
  @ndb.synctasklet
  def default_language(self):
    user = self.users.get_current_user()
    if user is not None:
      if hasattr(user, "language") and user.language is not None:
        raise ndb.Return(user.language)
      else:
        key = ndb.Key(model.User, user.user_id())
        entity = yield key.get_async()
        if entity is not None and hasattr(entity, "language") and entity.language is not None:
          raise ndb.Return(entity.language)
    raise ndb.Return("en")

class Index(BaseHandler):
  @tap.head(angular, bootstrap)
  @tap.session_read_only
  def get(self):
    language_list = self.language_list
    self.render_response("index.html", locals())

class Settings(BaseHandler):
  @tap.head(angular, bootstrap)
  @tap.csrf
  @tap.session
  def get(self):
    user = self.users.get_current_user()
    if user is not None:
      key = ndb.Key(model.User, user.user_id())
      entity = yield key.get_async()
      if entity is not None:
        user.name = entity.name
        user.language = entity.language
        user.set_to_session(self.session)
    language_list = self.language_list
    self.render_response("settings.html", locals())

  @tap.head(angular, bootstrap)
  @tap.csrf
  @tap.session
  def post(self):
    user = self.users.get_current_user()
    if user is not None:
      name = self.request.POST.get("name")
      if name is not None:
        user.name = name
      language = self.request.POST.get("language")
      if language is not None:
        user.language = language
      user.set_to_session(self.session)
      future = api_user.store(user)
      if future.check_success():
        logging.error(future.get_exception())
        self.abort(500)
      self.redirect(webapp2.uri_for("settings"))
    language_list = self.language_list
    self.render_response("settings.html", locals())

routes = [
  webapp2.Route("/", Index, name="index"),
  webapp2.Route("/settings", Settings, name="settings"),
]
