from datetime import datetime

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

  @endpoints.method(message.IssueReceiveNew, message.IssueSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = tap.endpoints.get_user_from_endpoints_service(self)
    if session_user is None:
      raise

    user_key = ndb.Key(model.User, session_user.user_id())
    project_key = ndb.Key(model.Project, int(request.project))
    if request.assignee is not None:
      assignee_key = ndb.Key(model.User, request.assignee)
      user, project, assignee = yield ndb.get_multi_async((user_key, project_key, assignee_key))
    else:
      assignee_key = None
      user, project = yield ndb.get_multi_async((user_key, project_key))

    if not user:
      raise
    if not project:
      raise
    if not user.key in project.member:
      raise
    if assignee_key is not None and not assignee:
      raise

    issue_key = model.Issue.gen_key(
      project_key   = project_key,
      will_start_at = datetime.now(),
      author        = user,
    )
    issue = model.Issue(
      key           = issue_key          ,
      subject       = request.subject       ,
      description   = request.description   ,
      assignee      = assignee_key      ,
    )
    _issue_key = yield issue.put_async()

    raise ndb.Return(message.IssueSend(
      project       = issue.project_key.integer_id()  ,
      subject       = issue.subject      ,
      description   = issue.description  ,
      assignee      = issue.assignee.integer_id() if issue.assignee else None     ,
      key           = issue.key.string_id(),
      closed_on     = issue.closed_on    ,
      will_start_at = issue.will_start_at,
      author        = issue.author_key.integer_id()       ,
    ))
