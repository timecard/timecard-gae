from datetime import datetime

import utils

from js.bootstrap import bootstrap
import webapp2

class BaseHandler(utils.RequestHandler):
  i18n = True
  i18n_domain = "timecard"

class Index(BaseHandler):
  @utils.head(bootstrap)
  @utils.session_read_only
  def get(self):
    name = self.session.get("name")
    is_signin = name is not None
    self.render_response("index.html", locals())

class Settings(BaseHandler):
  @utils.head(bootstrap)
  @utils.session_read_only
  def get(self):
    name = self.session.get("name")
    is_signin = name is not None
    self.render_response("settings.html", locals())

  @utils.head(bootstrap)
  @utils.session
  def post(self):
    name = self.session.get("name")
    is_signin = name is not None
    self.render_response("settings.html", locals())

routes = [
  webapp2.Route("/", Index, name="index"),
  webapp2.Route("/settings", Settings, name="settings"),
]
