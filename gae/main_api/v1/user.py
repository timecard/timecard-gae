from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap
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

  @endpoints.method(message.UserReceiveListCollection, message.UserSendCollection)
  @ndb.synctasklet
  def list(self, request):
    user_key_list = list()
    for user_receive_list in request.items:
      user_key_list.append(ndb.Key(model.User, user_receive_list.key))
    if user_key_list:
      if request.pagination:
        raise BadRequestException()
      entities = yield ndb.get_multi_async(user_key_list)
      cursor = more = None
    else:
      entities, cursor, more = yield tap.fetch_page_async(
        query = model.User.query(),
        cursor_string = request.pagination,
        page = 20,
      )
    items = list()
    for user in entities:
      items.append(message.UserSend(key=user.user_id,
                                    name=user.name,
                                    language=user.language))
    raise ndb.Return(message.UserSendCollection(
      items = items,
      pagination = cursor.urlsafe() if more else None,
    ))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    user = yield user_key.get_async()
    if user is not None:
      raise endpoints.ForbiddenException()

    user.name = request.name
    user.language = request.language
    future = user.put_async()
    if future.check_success():
      raise future.get_exception()
    raise ndb.Return(message.UserSend(key=user.user_id,
                                      name=user.name,
                                      language=user.language))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    user = yield user_key.get_async()
    if user is None:
      raise endpoints.BadRequestException()

    user.name = request.name
    user.language = request.language
    future = user.put_async()
    if future.check_success():
      raise future.get_exception()
    raise ndb.Return(message.UserSend(key=user.user_id,
                                      name=user.name,
                                      language=user.language))
