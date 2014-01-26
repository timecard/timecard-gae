from google.appengine.api import search
from google.appengine.ext import (
  deferred,
  ndb,
)
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model

from api import api
import message

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
    if len(request.query.encode("utf-8")) < 3:
      raise endpoints.BadRequestException("Bad query")
    query = search.Query(
      query_string = request.query,
      options = search.QueryOptions(
        limit  = 20,
        cursor = search.Cursor(web_safe_string=request.pagination),
        ids_only = True,
      ),
    )
    key_list = list()
    documents = UserSearchIndex.search_index.search(query)
    for document in documents:
      key_list.append(ndb.Key(model.User, document.doc_id))
    items = list()
    if key_list:
      entities = yield ndb.get_multi_async(key_list)
      for user in entities:
        items.append(message.UserSend(key=user.user_id,
                                      name=user.name,
                                      language=user.language))
    if documents.cursor:
      cursor_string = documents.cursor.web_safe_string
    else:
      cursor_string = None
    raise ndb.Return(message.UserSendCollection(
      items = items,
      pagination = cursor_string,
    ))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def create(self, request):
    user_key = ndb.Key(model.User, self._get_user_key_id())
    entity = yield user_key.get_async()
    if entity is not None:
      raise endpoints.ForbiddenException()

    entity = model.User(
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
    user_key = ndb.Key(model.User, self._get_user_key_id())
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
    deferred.defer(cls.put, user.user_id, user.name)

  @classmethod
  def put(cls, doc_id, name):
    cls.search_index.put(search.Document(
      doc_id = doc_id,
      fields = [search.TextField(name="a", value=name)],
    ))
