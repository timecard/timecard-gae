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

#package = "timecard"

@endpoints.api(name="timecard", version="v1")
class ProjectAPI(remote.Service):

  @endpoints.method(message_types.VoidMessage, message.ProjectSend,
                    path="projects", http_method="GET",
                    name="timecard.projects")
  def greetings_list(self, _request):
    return message.ProjectSendCollection()

api_services = [
  ProjectAPI,
]
