from datetime import datetime

import utils

from js.bootstrap import bootstrap
import webapp2

class SignIn(utils.RequestHandler):
  i18n = True
  i18n_domain = "timecard-users"

  @utils.head(bootstrap)
  #@utils.cache(60)
  def get(self, subdomain=None):
    self.render_response("sign_in.html", locals())

routes = [
  webapp2.Route("/sign_in", SignIn),
]
