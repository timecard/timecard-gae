from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model

from . import message
from .api import api

@ndb.tasklet
def user_store(user):
  key = ndb.Key(model.User, user.user_id())
  entity = yield key.get_async()
  if entity is None:
    entity = model.User(key=key)
  entity.name = user.name
  entity.language = user.language
  entity.put_async()

@api.api_class(resource_name="user", path="user")
class User(tap.endpoints.CRUDService):

  @endpoints.method(message_types.VoidMessage, message.UserSendCollection)
  @ndb.synctasklet
  def list(self, _request):
    items = list()
    entities = yield model.User.query().fetch_async()
    for user in entities:
      items.append(message.UserSend(user_id=user.user_id,
                                    name=user.name,
                                    language=user.language))
    raise ndb.Return(message.UserSendCollection(items=items))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()
    key = ndb.Key(model.User, session_user.user_id())
    user = yield key.get_async()
    if user is not None:
      raise endpoints.UnauthorizedException()
    user.name = request.name
    user.language = request.language
    future = user.put_async()
    if future.check_success():
      raise future.get_exception()
    raise ndb.Return(message.UserSend(user_id=user.user_id,
                                      name=user.name,
                                      language=user.language))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()
    key = ndb.Key(model.User, session_user.user_id())
    user = yield key.get_async()
    if user is None:
      raise endpoints.UnauthorizedException()
    user.name = request.name
    user.language = request.language
    future = user.put_async()
    if future.check_success():
      raise future.get_exception()
    raise ndb.Return(message.UserSend(user_id=user.user_id,
                                      name=user.name,
                                      language=user.language))
