from google.appengine.ext import ndb
from protorpc import (
  message_types,
)
import endpoints
import tap
import tap.endpoints

import main_model as model

from . import message
from .api import api

@api.api_class(resource_name="project", path="project")
class Project(tap.endpoints.CRUDService):

  @endpoints.method(message.ProjectReceiveList, message.ProjectSendCollection)
  @ndb.synctasklet
  def list(self, request):
    session_user = self._get_user()
    if session_user is None:
      user = None
    else:
      user_key = ndb.Key(model.User, session_user.user_id())
      user = yield user_key.get_async()

    if user:
      query = model.Project.query(ndb.OR(model.Project.is_public == True,
                                         model.Project.member == user_key))
      query = query.order(model.Project.key)
    else:
      query = model.Project.query(model.Project.is_public == True)
    entities, cursor, more = yield tap.fetch_page_async(
      query = query,
      cursor_string = request.pagination,
      page = 20,
    )

    items = list()
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
    raise ndb.Return(message.ProjectSendCollection(
      items = items,
      pagination = cursor.urlsafe() if more else None,
    ))

  @endpoints.method(message.ProjectReceiveNew, message.ProjectSend)
  @ndb.synctasklet
  def create(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    user = yield user_key.get_async()
    if user is None:
      raise endpoints.UnauthorizedException()

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

  @endpoints.method(message.ProjectReceive, message.ProjectSend)
  @ndb.synctasklet
  def update(self, request):
    session_user = self._get_user()
    if session_user is None:
      raise endpoints.UnauthorizedException()

    user_key = ndb.Key(model.User, session_user.user_id())
    project_key = ndb.Key(model.Project, request.key)
    user, project = yield ndb.get_multi_async((user_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not project:
      raise endpoints.NotFoundException()
    if not user.key in project.admin:
      raise endpoints.ForbiddenException()

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
