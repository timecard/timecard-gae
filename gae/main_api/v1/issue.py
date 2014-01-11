from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model
import main_message as message

from .api import api

@api.api_class(resource_name="issue", path="issue")
class Issue(tap.endpoints.CRUDService):

  @endpoints.method(message_types.VoidMessage, message.IssueSendCollection)
  @ndb.synctasklet
  def list(self, _request):
    items = list()
    entities = yield model.Issue.query().fetch_async()
    for issue in entities:
      items.append(message.IssueSend(
        project       = issue.project_key.integer_id()      ,
        subject       = issue.subject      ,
        description   = issue.description  ,
        assignee      = issue.assignee.integer_id()     ,
        key           = issue.key.string_id()          ,
        closed_on     = issue.closed_on    ,
        will_start_at = issue.will_start_at,
        author        = issue.author.key.integer_id()       ,
      ))
    raise ndb.Return(message.IssueSendCollection(items=items))
