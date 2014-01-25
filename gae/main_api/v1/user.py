from google.appengine.api import search
from google.appengine.ext import (
  deferred,
  ndb,
)
from protorpc import (
  message_types,
)
import endpoints
import tap
import tap.endpoints

import main_model as model

from . import message
from .api import api

class user(object):
  @staticmethod
  @ndb.tasklet
  def store(user):
    key = ndb.Key(model.User, user.user_id())
    entity = yield key.get_async()
    if entity is None:
      entity = model.User(key=key)
    entity.name = user.name
    entity.language = user.language
    entity.put_async()
    UserSearchIndex.update(user)

@api.api_class(resource_name="user", path="user")
class User(tap.endpoints.CRUDService):

  @endpoints.method(message.UserReceiveListCollection, message.UserSendCollection)
  @ndb.synctasklet
  def list(self, request):
    key_list = list()
    for user_receive_list in request.items:
      key_list.append(ndb.Key(model.User, user_receive_list.key))
    if key_list:
      entities = yield ndb.get_multi_async(key_list)
    else:
      raise endpoints.BadRequestException("Bad query")
    items = list()
    for user in entities:
      items.append(message.UserSend(key=user.user_id,
                                    name=user.name,
                                    language=user.language))
    raise ndb.Return(message.UserSendCollection(
      items = items,
    ))

  @endpoints.method(message.UserReceiveSearch, message.UserSendCollection)
  @ndb.synctasklet
  def search(self, request):
    if len(request.search) < 3:
      raise endpoints.BadRequestException("Bad query")
    key_list = list()
    for document in UserSearchIndex.search_index.search(request.search):
      key_list.append(ndb.Key(model.User, document.doc_id))
    items = list()
    if key_list:
      entities = yield ndb.get_multi_async(key_list)
      for user in entities:
        items.append(message.UserSend(key=user.user_id,
                                      name=user.name,
                                      language=user.language))
    raise ndb.Return(message.UserSendCollection(
      items = items,
    ))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    entity = yield user_key.get_async()
    if entity is not None:
      raise endpoints.ForbiddenException()

    entity = ndb.User(
      key       = user_key,
      name      = request.name,
      language  = request.language,
    )
    future = entity.put_async()
    if future.check_success():
      raise future.get_exception()
    UserSearchIndex.update(entity)
    raise ndb.Return(message.UserSend(
      key       = entity.key.string_id(),
      name      = entity.name,
      language  = entity.language,
    ))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    entity = yield user_key.get_async()
    if entity is None:
      raise endpoints.BadRequestException()

    entity.name = request.name
    entity.language = request.language
    future = entity.put_async()
    if future.check_success():
      raise future.get_exception()
    UserSearchIndex.update(entity)
    raise ndb.Return(message.UserSend(
      key       = entity.key.string_id(),
      name      = entity.name,
      language  = entity.language,
    ))

class UserSearchIndex(object):

  search_index = search.Index(name="timecard:user")

  @classmethod
  def update(cls, user):
    if user.language == "ja":
      queue = "yahoo-japan-jlp-ma"
    else:
      queue = "default"
    deferred.defer(cls.put,
                   user.user_id(), user.name, user.language,
                   _queue=queue)

  @classmethod
  def put(cls, doc_id, name, language):
    if language == "ja":
      from .util import jlp_api
      fields = [search.TextField(name="a", value=word, language=language) for word in jlp_api.ma(name)]
    else:
      fields = [search.TextField(name="a", value=name, language=language)]
    cls.search_index.put(search.Document(
      doc_id = doc_id,
      fields = fields,
    ))
