from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model
import main_message as message

@ndb.tasklet
def user_store(user):
  key = ndb.Key(model.User, user.user_id())
  entity = yield key.get_async()
  if entity is None:
    entity = model.User(key=key)
  entity.name = user.name
  entity.language = user.language
  entity.put_async()

api = endpoints.api(name="timecard", version="v1")

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
    session_user = tap.endpoints.get_user_from_endpoints_service(self)
    if session_user is None:
      raise
    key = ndb.Key(model.User, session_user.user_id())
    user = yield key.get_async()
    if user is not None:
      raise
    user.name = request.name
    user.language = request.language
    future = user.put_async()
    if future.check_success():
      raise future.get_exception()
    raise ndb.Return(message.UserSend(user_id=user.user_id,
                                      name=user.name,
                                      language=user.language))

  @endpoints.method(message_types.VoidMessage, message.UserSend)
  def read(self, _request):
    return message.UserSendCollection()

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = tap.endpoints.get_user_from_endpoints_service(self)
    if session_user is None:
      raise
    key = ndb.Key(model.User, session_user.user_id())
    user = yield key.get_async()
    if user is None:
      raise
    user.name = request.name
    user.language = request.language
    future = user.put_async()
    if future.check_success():
      raise future.get_exception()
    raise ndb.Return(message.UserSend(user_id=user.user_id,
                                      name=user.name,
                                      language=user.language))

  @endpoints.method(message_types.VoidMessage, message.UserSend)
  def delete(self, _request):
    return message.UserSendCollection()

@api.api_class(resource_name="project", path="project")
class Project(tap.endpoints.CRUDService):

  @endpoints.method(message_types.VoidMessage, message.ProjectSend)
  def list(self, _request):
    return message.ProjectSendCollection()

  @endpoints.method(message_types.VoidMessage, message.ProjectSend, name="create")
  def create(self, _request):
    return message.ProjectSendCollection()

  @endpoints.method(message_types.VoidMessage, message.ProjectSend)
  def read(self, _request):
    return message.ProjectSendCollection()

  @endpoints.method(message_types.VoidMessage, message.ProjectSend)
  def update(self, _request):
    return message.ProjectSendCollection()

  @endpoints.method(message_types.VoidMessage, message.ProjectSend)
  def delete(self, _request):
    return message.ProjectSendCollection()

api_services = [api]
