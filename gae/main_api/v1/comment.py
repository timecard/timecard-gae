from datetime import datetime

from google.appengine.ext import ndb
from protorpc import message_types
import endpoints
import tap.endpoints

import main_model as model
import main_message as message

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
        body          = comment.body,
        issue         = comment.issue_key.string_id(),
        project       = comment.project_key.integer_id(),
        time_at       = comment.time_at,
        author        = comment.author_key.string_id(),
        author_name   = comment.author_name,
      ))
    raise ndb.Return(message.CommentSendCollection(items=items))
