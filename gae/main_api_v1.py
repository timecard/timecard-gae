from google.appengine.ext import ndb
from protorpc import (
  message_types,
  remote,
)
import endpoints

import main_model as model
import main_message as message

@ndb.tasklet
def user_store(user):
  key = ndb.Key(model.User, user.user_id())
  entity = yield key.get_async()
  if entity is None:
    entity = model.User(key=key)
  entity.name = user.name
  yield entity.put_async()

api = endpoints.api(name="timecard", version="v1")

@api.api_class(resource_name="user", path="user")
class User(remote.Service):

  @endpoints.method(message_types.VoidMessage, message.UserSendCollection)
  @ndb.synctasklet
  def list(self, _request):
    items = list()
    entities = yield model.User.query().fetch_async()
    for user in entities:
      user.set_from_key() #TODO
      items.append(message.UserSend(user_id=user.user_id, name=user.name))
    raise ndb.Return(message.UserSendCollection(items=items))

  @endpoints.method(message.UserReceive, message.UserSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = utils.get_user_from_endpoints_service(self)
    key = ndb.Key(model.User, session_user.user_id())
    user = yield key.get_async()
    if user is not None:
      raise
    user.name = session_user.name
    yield user.put_async()
    raise ndb.Return(message.UserSend(user_id=user.user_id(), name=user.name))

  @endpoints.method(message_types.VoidMessage, message.UserSend)
  def read(self, _request):
    return message.UserSendCollection()

  @endpoints.method(message_types.VoidMessage, message.UserSend)
  def update(self, _request):
    return message.UserSendCollection()

  @endpoints.method(message_types.VoidMessage, message.UserSend)
  def delete(self, _request):
    return message.UserSendCollection()

@api.api_class(resource_name="project", path="project")
class Project(remote.Service):

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
