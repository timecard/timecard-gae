from google.appengine.ext import ndb
from protorpc import (
  message_types,
  messages,
  remote,
)
import endpoints

import main_model as model

@ndb.tasklet
def user_store(user):
  key = ndb.Key(model.User, user.user_id())
  entity = yield key.get_async()
  if entity is None:
    entity = model.User(key=key)
  entity.name = user.name
  yield entity.put_async()

class ProjectSend(messages.Message):
  name        = messages.StringField (1, required=True)
  description = messages.StringField (2, required=True)
  is_public   = messages.BooleanField(3, required=True)
  closed      = messages.BooleanField(4, required=True)
  archive     = messages.BooleanField(5, required=True)
  admin       = messages.StringField (6, repeated=True)
  member      = messages.StringField (7, repeated=True)

class ProjectReceive(messages.Message):
  name        = messages.StringField (1, required=True)
  description = messages.StringField (2, required=True)

class ProjectSendCollection(messages.Message):
  items = messages.MessageField(ProjectSend, 1, repeated=True)

#package = "timecard"

@endpoints.api(name="timecard", version="v1")
class ProjectAPI(remote.Service):

  @endpoints.method(message_types.VoidMessage, ProjectSend,
                    path="projects", http_method="GET",
                    name="timecard.projects")
  def greetings_list(self, _request):
    return ProjectSendCollection()

api_services = [
  ProjectAPI,
]
