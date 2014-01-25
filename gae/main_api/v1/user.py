# -*- coding: utf-8 -*-
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

search_index = search.Index(name="timecard:user")

class user(object):
  @staticmethod
  @ndb.tasklet
  def store(user_store):
    cls = user
    key = ndb.Key(model.User, user_store.user_id())
    entity = yield key.get_async()
    if entity is None:
      entity = model.User(key=key)
    entity.name = user_store.name
    entity.language = user_store.language
    entity.put_async()
    if user_store.language == "ja":
      queue = "yahoo-japan-jlp-ma"
    else:
      queue = "default"
    deferred.defer(cls.update_search_index,
                   user_store.user_id(), user_store.name, user_store.language,
                   _queue=queue)

  @classmethod
  def update_search_index(cls, user_id, name, language):
    if language == "ja":
      from .util import jlp_api
      result_set = jlp_api.ma.get_result_set(name)
      words = filter(lambda x: x.pos not in (u"助詞", u"特殊"), result_set.ma_result.words)
      fields = [search.TextField(name="name", value=word.surface, language=language) for word in words]
    else:
      fields = [search.TextField(name="name", value=name, language=language)]
    search_index.put(search.Document(
      doc_id = user_id,
      fields = fields,
    ))

@api.api_class(resource_name="user", path="user")
class User(tap.endpoints.CRUDService):

  @endpoints.method(message.UserReceiveListCollection, message.UserSendCollection)
  @ndb.synctasklet
  def list(self, request):
    if len(filter(lambda x:x is not None, [len(request.items) or None, request.search, request.pagination])) != 1:
      raise endpoints.BadRequestException("Bad query")
    user_key_list = list()
    for user_receive_list in request.items:
      user_key_list.append(ndb.Key(model.User, user_receive_list.key))
    if user_key_list:
      entities = yield ndb.get_multi_async(user_key_list)
      cursor = more = None
    elif request.search not in [None, ""]:
      for document in search_index.search(request.search):
        user_key_list.append(ndb.Key(model.User, document.doc_id))
      entities = yield ndb.get_multi_async(user_key_list)
      cursor = more = None
    elif request.pagination not in [None, ""]:
      entities, cursor, more = yield tap.fetch_page_async(
        query = model.User.query(),
        cursor_string = request.pagination,
        page = 20,
      )
    else:
      raise endpoints.BadRequestException("Bad query")
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
