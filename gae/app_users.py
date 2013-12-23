from datetime import datetime

import utils

from js.bootstrap import bootstrap
import webapp2

class SignIn(utils.RequestHandler):
  i18n = True
  i18n_domain = "timecard-users"

  @utils.head(bootstrap)
  @utils.session_read_only
  def get(self, subdomain=None):
    name = self.session.get("name")
    is_signin = name is not None
    self.render_response("sign_in.html", locals())

routes = [
  webapp2.Route("/sign_in", SignIn),
]
