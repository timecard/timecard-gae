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

@api.api_class(resource_name="workload", path="workload")
class WorkLoad(tap.endpoints.CRUDService):

  @endpoints.method(message_types.VoidMessage, message.WorkLoadSendCollection)
  @ndb.synctasklet
  def list(self, _request):
    items = list()
    entities = yield model.WorkLoad.query().fetch_async()
    for workload in entities:
      items.append(message.WorkLoadSend(
        issue         = workload.issue_key.string_id(),
        end_at        = workload.end_at,
        user          = workload.user.string_id(),
        active        = workload.active,
        project       = workload.project_key.integer_id(),
        start_at      = workload.start_at,
        project_name  = workload.project_name,
        issue_subject = workload.issue_subject,
      ))
    raise ndb.Return(message.WorkLoadSendCollection(items=items))

  @endpoints.method(message.WorkLoadReceiveNew, message.WorkLoadSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = tap.endpoints.get_user_from_endpoints_service(self)
    if session_user is None:
      raise

    user_key = ndb.Key(model.User, session_user.user_id())
    issue_key = ndb.Key(model.Issue, request.issue)
    project_key, _will_start_at, _user_id, _name = model.Issue.parse_key(issue_key)
    user, issue, project = yield ndb.get_multi_async((user_key, issue_key, project_key))

    if not user:
      raise
    if not issue:
      raise
    if not project:
      raise
    if user.key not in project.member:
      raise

    workload_key = model.WorkLoad.gen_key(
      project_key = project_key,
      issue_key   = issue_key,
      start_at    = datetime.now(),
    )
    workload = model.WorkLoad(
      key  = workload_key ,
      user = user_key,
    )
    _workload_key = yield workload.put_async()

    raise ndb.Return(message.WorkLoadSend(
      issue         = workload.issue_key.string_id(),
      end_at        = workload.end_at,
      user          = workload.user.string_id(),
      active        = workload.active,
      project       = workload.project_key.integer_id(),
      start_at      = workload.start_at,
      project_name  = workload.project_name,
      issue_subject = workload.issue_subject,
    ))
