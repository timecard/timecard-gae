from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model
import main_message as message

from .api import api

@api.api_class(resource_name="project", path="project")
class Project(tap.endpoints.CRUDService):

  @endpoints.method(message_types.VoidMessage, message.ProjectSendCollection)
  @ndb.synctasklet
  def list(self, _request):
    items = list()
    entities = yield model.Project.query().fetch_async()
    for project in entities:
      items.append(message.ProjectSend(
        key         = project.key.integer_id(),
        name        = project.name       ,
        description = project.description,
        is_public   = project.is_public  ,
        closed      = project.closed     ,
        archive     = project.archive    ,
        admin       = [key.string_id() for key in project.admin],
        member      = [key.string_id() for key in project.member],
      ))
    raise ndb.Return(message.ProjectSendCollection(items=items))

  @endpoints.method(message.ProjectReceiveNew, message.ProjectSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = tap.endpoints.get_user_from_endpoints_service(self)
    if session_user is None:
      raise
    key = ndb.Key(model.User, session_user.user_id())
    user = yield key.get_async()
    if user is None:
      raise

    project = model.Project(
      name        = request.name       ,
      description = request.description,
      is_public   = request.is_public  ,
      admin       = (user.key,)        ,
      member      = (user.key,)        ,
    )
    _project_key = yield project.put_async()

    raise ndb.Return(message.ProjectSend(
      key         = project.key.integer_id(),
      name        = project.name       ,
      description = project.description,
      is_public   = project.is_public  ,
      closed      = project.closed     ,
      archive     = project.archive    ,
      admin       = [key.string_id() for key in project.admin],
      member      = [key.string_id() for key in project.member],
    ))

  @endpoints.method(message_types.VoidMessage, message.ProjectSend)
  def read(self, _request):
    return message.ProjectSendCollection()

  @endpoints.method(message.ProjectReceive, message.ProjectSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = tap.endpoints.get_user_from_endpoints_service(self)
    if session_user is None:
      raise

    user_key = ndb.Key(model.User, session_user.user_id())
    project_key = ndb.Key(model.Project, request.key)
    user, project = yield ndb.get_multi_async((user_key, project_key))

    if not user:
      raise
    if not project:
      raise
    if not user.key in project.admin:
      raise

    project.name        = request.name
    project.description = request.description
    project.is_public   = request.is_public
    project.closed      = request.closed
    project.archive     = request.archive
    project.admin       = request.admin
    project.member      = request.member
    _project_key = yield project.put_async()

    raise ndb.Return(message.ProjectSend(
      key         = project.key.integer_id(),
      name        = project.name       ,
      description = project.description,
      is_public   = project.is_public  ,
      closed      = project.closed     ,
      archive     = project.archive    ,
      admin       = project.admin      ,
      member      = project.member     ,
    ))

  @endpoints.method(message_types.VoidMessage, message.ProjectSend)
  def delete(self, _request):
    return message.ProjectSendCollection()