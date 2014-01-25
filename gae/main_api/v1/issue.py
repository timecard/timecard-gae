from datetime import datetime

from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model

from . import message
from .api import api

@api.api_class(resource_name="issue", path="issue")
class Issue(tap.endpoints.CRUDService):

  @endpoints.method(message.IssueReceiveList, message.IssueSendCollection)
  @ndb.synctasklet
  def list(self, request):
    project_key = ndb.Key(model.Project, request.project)
    session_user = self._get_user()
    if session_user is None:
      user = None
      project = yield project_key.get_async()
    else:
      user_key = ndb.Key(model.User, session_user.user_id())
      user, project = yield ndb.get_multi_async((user_key, project_key))

    if not project:
      raise endpoints.NotFoundException()
    if not project.is_public and (not user or user.key not in project.member):
      raise endpoints.ForbiddenException()

    project_id = project.key.integer_id()
    key_start = ndb.Key(model.Issue, project_id)
    key_end   = ndb.Key(model.Issue, "{0}/\xff".format(project_id))
    query = model.Issue.query(ndb.AND(model.Issue.key >= key_start,
                                      model.Issue.key <= key_end))
    entities, cursor, more = yield tap.fetch_page_async(
      query = query,
      cursor_string = request.pagination,
      page = 20,
    )

    items = list()
    for issue in entities:
      items.append(message.IssueSend(
        project       = issue.project_key.integer_id()      ,
        subject       = issue.subject      ,
        description   = issue.description  ,
        assignee      = issue.assignee.integer_id() if issue.assignee else None     ,
        key           = issue.key.string_id()          ,
        closed_on     = issue.closed_on    ,
        will_start_at = issue.will_start_at,
        author        = issue.author_key.integer_id()       ,
      ))
    raise ndb.Return(message.IssueSendCollection(
      items = items,
      pagination = cursor.urlsafe() if more else None,
    ))

  @endpoints.method(message.IssueReceiveNew, message.IssueSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    project_key = ndb.Key(model.Project, int(request.project))
    if request.assignee is not None:
      assignee_key = ndb.Key(model.User, request.assignee)
      user, project, assignee = yield ndb.get_multi_async((user_key, project_key, assignee_key))
    else:
      assignee_key = None
      user, project = yield ndb.get_multi_async((user_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not project:
      raise endpoints.BadRequestException()
    if not user.key in project.member:
      raise endpoints.ForbiddenException()
    if assignee_key is not None and not assignee:
      raise endpoints.BadRequestException()

    issue_key = model.Issue.gen_key(
      project_key   = project_key,
      will_start_at = datetime.utcnow(),
      author_id     = user.key.string_id(),
      author_name   = user.name,
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

  @endpoints.method(message.IssueReceive, message.IssueSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    issue_key = ndb.Key(model.Issue, request.key)
    project_key, _will_start_at, _user_id, _name = model.Issue.parse_key(issue_key)
    user, issue, project = yield ndb.get_multi_async((user_key, issue_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not issue:
      raise endpoints.NotFoundException()
    if user.key not in project.member:
      raise endpoints.ForbiddenException()

    issue.subject     = request.subject
    issue.description = request.description
    issue.closed_on   = request.closed_on
    issue.assignee    = ndb.Key(model.User, int(request.assignee)) if issue.assignee else None
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

  @endpoints.method(message.IssueReceiveToggle, message.IssueSend)
  @ndb.synctasklet
  def close(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    issue_key = ndb.Key(model.Issue, request.key)
    project_key, _will_start_at, _user_id, _name = model.Issue.parse_key(issue_key)
    user, issue, project = yield ndb.get_multi_async((user_key, issue_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not issue:
      raise endpoints.NotFoundException()
    if user.key not in project.member:
      raise endpoints.ForbiddenException()

    issue.closed_on   = datetime.utcnow()
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

  @endpoints.method(message.IssueReceiveToggle, message.IssueSend)
  @ndb.synctasklet
  def reopen(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    issue_key = ndb.Key(model.Issue, request.key)
    project_key, _will_start_at, _user_id, _name = model.Issue.parse_key(issue_key)
    user, issue, project = yield ndb.get_multi_async((user_key, issue_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not issue:
      raise endpoints.NotFoundException()
    if user.key not in project.member:
      raise endpoints.ForbiddenException()

    issue.closed_on   = None
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
