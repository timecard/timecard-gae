from google.appengine.ext import ndb

class User(ndb.Model):
  #key = ndb.StringProperty()
  name = ndb.StringProperty()
  #not_do_today = list of Issue
