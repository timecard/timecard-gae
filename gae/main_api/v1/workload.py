from datetime import datetime
import operator

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

  @endpoints.method(message.WorkLoadReceive, message.WorkLoadSendCollection)
  @ndb.synctasklet
  def list(self, request):
    items = list()
    if request.active:
      query = model.ActiveWorkLoad.query()
    else:
      query = model.WorkLoad.query()
    entities = yield query.fetch_async()
    for workload in entities:
      items.append(message.WorkLoadSend(
        issue         = workload.issue_key.string_id(),
        end_at        = workload.end_at if hasattr(workload, "end_at") else None,
        user          = workload.user.string_id(),
        project       = workload.project_key.integer_id(),
        start_at      = workload.start_at,
        project_name  = workload.project_name,
        issue_subject = workload.issue_subject,
      ))
    raise ndb.Return(message.WorkLoadSendCollection(items=items))

  @endpoints.method(message.WorkLoadReceiveNew, message.WorkLoadSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise

    user_id = session_user.user_id()
    user_key = ndb.Key(model.User, user_id)
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

    key_start = ndb.Key(model.ActiveWorkLoad, user_id)
    key_end   = ndb.Key(model.ActiveWorkLoad, "{0}/\xff".format(user_id))
    query = model.ActiveWorkLoad.query(ndb.AND(model.ActiveWorkLoad.key >= key_start,
                                               model.ActiveWorkLoad.key <= key_end))
    activeworkload = yield query.get_async()

    if activeworkload:
      raise

    activeworkload_key = model.ActiveWorkLoad.gen_key(
      project_key = project_key,
      issue_key   = issue_key,
      start_at    = datetime.utcnow(),
      user_key    = user.key,
      user_name   = user.name,
    )
    activeworkload = model.ActiveWorkLoad(
      key  = activeworkload_key ,
    )
    _activeworkload_key = yield activeworkload.put_async()

    raise ndb.Return(message.WorkLoadSend(
      issue         = activeworkload.issue_key.string_id(),
      end_at        = None,
      user          = user.key.string_id(),
      project       = activeworkload.project_key.integer_id(),
      start_at      = activeworkload.start_at,
      project_name  = activeworkload.project_name,
      issue_subject = activeworkload.issue_subject,
    ))

  @endpoints.method(message_types.VoidMessage, message.WorkLoadSend)
  def read(self, _request):
    return message.WorkLoadSendCollection()

  @endpoints.method(message.WorkLoadReceiveClose, message.WorkLoadSend)
  @ndb.synctasklet
  def update(self, _request):
    session_user = self._get_user()
    if session_user is None:
      raise

    user_id = session_user.user_id()
    user_key = ndb.Key(model.User, user_id)
    user = yield user_key.get_async()

    if not user:
      raise

    key_start = ndb.Key(model.ActiveWorkLoad, user_id)
    key_end   = ndb.Key(model.ActiveWorkLoad, "{0}/\xff".format(user_id))
    query = model.ActiveWorkLoad.query(ndb.AND(model.ActiveWorkLoad.key >= key_start,
                                               model.ActiveWorkLoad.key <= key_end))
    activeworkload_key_list = yield query.fetch_async(keys_only=True)

    if not activeworkload_key_list:
      raise

    activeworkload_list = list()
    for activeworkload_key in activeworkload_key_list:
      (
        project_key,
        issue_key,
        start_at,
        user_key,
        user_name,
        project_name,
        issue_subject,
      ) = model.ActiveWorkLoad.parse_key(activeworkload_key)
      activeworkload_list.append((activeworkload_key, start_at,
                                  project_key,
                                  issue_key,
                                  user_key,
                                  user_name,
                                  project_name,
                                  issue_subject,
                                 ))
    start_at = None
    end_at = datetime.utcnow()
    workload_list = list()
    for activeworkload in sorted(activeworkload_list, key=operator.itemgetter(1), reverse=True):
      (activeworkload_key, start_at,
       project_key,
       issue_key,
       user_key,
       user_name,
       project_name,
       issue_subject,
      ) = activeworkload
      workload_list.append(model.WorkLoad(
        key = model.WorkLoad.gen_key(project_key, issue_key, start_at, start_at or end_at),
        user = user_key,
      ))

    @ndb.transactional(xg=True)
    @ndb.synctasklet
    def transaction():
      _activeworkload_key = yield ndb.delete_multi_async(activeworkload_key_list)
      _workload_key = yield ndb.put_multi_async(workload_list)

    transaction()

    raise ndb.Return(message.WorkLoadSend(
      issue         = issue_key.string_id(),
      end_at        = end_at,
      user          = user_key.string_id(),
      project       = project_key.integer_id(),
      start_at      = start_at,
      project_name  = project_name,
      issue_subject = issue_subject,
    ))

  @endpoints.method(message_types.VoidMessage, message.WorkLoadSend)
  def delete(self, _request):
    return message.WorkLoadSendCollection()
