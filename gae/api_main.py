from google.appengine.ext import ndb

class User(ndb.Model):
  #key = ndb.StringProperty()
  name = ndb.StringProperty()
  #not_do_today = list of Issue

@ndb.tasklet
def user_store(user):
  key = ndb.Key(User, user.user_id())
  entity = yield key.get_async()
  if entity is None:
    entity = User(key=key)
  entity.name = user.name
  yield entity.put_async()
