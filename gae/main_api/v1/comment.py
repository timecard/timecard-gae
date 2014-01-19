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

  @endpoints.method(message_types.VoidMessage, message.CommentSendCollection)
  @ndb.synctasklet
  def list(self, _request):
    items = list()
    entities = yield model.Comment.query().fetch_async()
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
      raise

    user_id = session_user.user_id()
    user_key = ndb.Key(model.User, user_id)
    comment_key = ndb.Key(model.Comment, request.key)
    user, comment = yield ndb.get_multi_async((user_key, comment_key))

    if not user:
      raise
    if not comment:
      raise
    if user.key != comment.author_key:
      raise

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
