from datetime import datetime

from google.appengine.ext import ndb
from protorpc import message_types
import endpoints
import tap.endpoints

import main_model as model

from . import message
from .api import api

@api.api_class(resource_name="comment", path="comment")
class Comment(tap.endpoints.CRUDService):

  @endpoints.method(message.CommentReceiveList, message.CommentSendCollection)
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

    if project.is_public or user and user.key in project.member:
      project_id = project.key.integer_id()
      key_start = ndb.Key(model.Comment, project_id)
      key_end   = ndb.Key(model.Comment, "{0}/\xff".format(project_id))
      query = model.Comment.query(ndb.AND(model.Comment.key >= key_start,
                                          model.Comment.key <= key_end))
      entities = yield query.fetch_async()
    else:
      entities = list()
    items = list()
    for comment in entities:
      items.append(message.CommentSend(
        issue         = comment.issue_key.string_id(),
        body          = comment.body,
        key           = comment.key.string_id(),
        project       = comment.project_key.integer_id(),
        time_at       = comment.time_at,
        author        = comment.author_key.string_id(),
        author_name   = comment.author_name,
        update_at     = comment.update_at if hasattr(comment, "update_at") else None,
      ))
    raise ndb.Return(message.CommentSendCollection(items=items))

  @endpoints.method(message.CommentReceive, message.CommentSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_id = session_user.user_id()
    user_key = ndb.Key(model.User, user_id)
    issue_key = ndb.Key(model.Issue, request.issue)
    project_key, _will_start_at, _user_id, _name = model.Issue.parse_key(issue_key)
    user, issue, project = yield ndb.get_multi_async((user_key, issue_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not issue:
      raise endpoints.BadRequestException()
    if not project:
      raise endpoints.BadRequestException()
    if user.key not in project.member:
      raise endpoints.ForbiddenException()

    time_at = datetime.utcnow()
    comment = model.Comment(
      key  = model.Comment.gen_key(issue_key, time_at, user_key, user.name),
      body = request.body,
    )
    _comment_key = yield comment.put_async()

    raise ndb.Return(message.CommentSend(
      issue         = comment.issue_key.string_id(),
      body          = comment.body,
      key           = comment.key.string_id(),
      project       = comment.project_key.integer_id(),
      time_at       = comment.time_at,
      author        = comment.author_key.string_id(),
      author_name   = comment.author_name,
      update_at     = comment.update_at if hasattr(comment, "update_at") else None,
    ))

  @endpoints.method(message.CommentReceiveUpdate, message.CommentSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_id = session_user.user_id()
    user_key = ndb.Key(model.User, user_id)
    comment_key = ndb.Key(model.Comment, request.key)
    user, comment = yield ndb.get_multi_async((user_key, comment_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not comment:
      raise endpoints.NotFoundException()
    if user.key != comment.author_key:
      raise endpoints.ForbiddenException()

    comment.body      = request.body
    comment.update_at = datetime.utcnow()
    _comment_key = yield comment.put_async()

    raise ndb.Return(message.CommentSend(
      issue         = comment.issue_key.string_id(),
      body          = comment.body,
      key           = comment.key.string_id(),
      project       = comment.project_key.integer_id(),
      time_at       = comment.time_at,
      author        = comment.author_key.string_id(),
      author_name   = comment.author_name,
      update_at     = comment.update_at if hasattr(comment, "update_at") else None,
    ))
