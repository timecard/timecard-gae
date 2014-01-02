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
