from google.appengine.api import (
  oauth,
  search,
)
from google.appengine.ext import (
  deferred,
  ndb,
)
from protorpc import (
  message_types,
)
import endpoints
import tap.endpoints

import main_model as model

from api import api
import message

rate_limit = tap.endpoints.rate_limit(rate=50, size=50, key=tap.endpoints.get_user_id, tag="timecard:api")

@api.api_class(resource_name="project", path="project")
class Project(tap.endpoints.CRUDService):

  @endpoints.method(message.ProjectReceiveList, message.ProjectSendCollection)
  @ndb.toplevel
  @rate_limit
  def list(self, request):
    import tap

    user_key = ndb.Key(model.User, tap.endpoints.get_user_id())
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
        language    = project.language      ,
      ))
    raise ndb.Return(message.ProjectSendCollection(
      items = items,
      pagination = cursor.urlsafe() if more else None,
    ))

  @endpoints.method(message.ProjectReceiveSearch, message.ProjectSendCollection)
  @ndb.toplevel
  @rate_limit
  def search(self, request):
    import tap
    if len(request.query.encode("utf-8")) < 3:
      raise endpoints.BadRequestException("Bad query")

    query = search.Query(
      query_string = request.query,
      options = search.QueryOptions(
        limit  = 20,
        cursor = search.Cursor(web_safe_string=request.pagination),
        ids_only = True,
      ),
    )

    key_list = list()
    documents = ProjectSearchIndex.search_index.search(query)
    for document in documents:
      key_list.append(ndb.Key(model.Project, tap.base62_decode(document.doc_id)))
    if key_list:
      entities = yield ndb.get_multi_async(key_list)
    else:
      entities = list()

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
        language    = project.language      ,
      ))

    if documents.cursor:
      cursor_string = documents.cursor.web_safe_string
    else:
      cursor_string = None

    raise ndb.Return(message.ProjectSendCollection(
      items = items,
      pagination = cursor_string,
    ))

  @endpoints.method(message.ProjectReceiveNew, message.ProjectSend)
  @ndb.toplevel
  @rate_limit
  def create(self, request):
    user_key = ndb.Key(model.User, tap.endpoints.get_user_id())
    user = yield user_key.get_async()
    if user is None:
      raise endpoints.UnauthorizedException()

    project = model.Project(
      name        = request.name       ,
      description = request.description,
      is_public   = request.is_public  ,
      admin       = (user.key,)        ,
      member      = (user.key,)        ,
      language    = user.language      ,
    )
    _project_key = yield project.put_async()

    if project.is_public:
      ProjectSearchIndex.update(project, will_un_public=False)

    raise ndb.Return(message.ProjectSend(
      key         = project.key.integer_id(),
      name        = project.name       ,
      description = project.description,
      is_public   = project.is_public  ,
      closed      = project.closed     ,
      archive     = project.archive    ,
      admin       = [key.string_id() for key in project.admin],
      member      = [key.string_id() for key in project.member],
      language    = project.language      ,
    ))

  @endpoints.method(message.ProjectReceive, message.ProjectSend)
  @ndb.toplevel
  @rate_limit
  def update(self, request):
    user_key = ndb.Key(model.User, tap.endpoints.get_user_id())
    project_key = ndb.Key(model.Project, request.key)
    user, project = yield ndb.get_multi_async((user_key, project_key))

    if not user:
      raise endpoints.UnauthorizedException()
    if not project:
      raise endpoints.NotFoundException()
    if not user.key in project.admin:
      raise endpoints.ForbiddenException()

    if request.is_public is False and request.is_public is True:
      will_un_public = True
    else:
      will_un_public = False

    project.name        = request.name
    project.description = request.description
    project.is_public   = request.is_public
    project.closed      = request.closed
    project.archive     = request.archive
    project.admin       = request.admin
    project.member      = request.member
    project.language    = request.language
    _project_key = yield project.put_async()

    ProjectSearchIndex.update(project, will_un_public)

    raise ndb.Return(message.ProjectSend(
      key         = project.key.integer_id(),
      name        = project.name       ,
      description = project.description,
      is_public   = project.is_public  ,
      closed      = project.closed     ,
      archive     = project.archive    ,
      admin       = project.admin      ,
      member      = project.member     ,
      language    = project.language      ,
    ))

class ProjectSearchIndex(object):

  search_index = search.Index(name="timecard:project")

  @classmethod
  def update(cls, project, will_un_public):
    import tap
    if project.is_public is False and will_un_public is False:
      return
    doc_id = tap.base62_encode(project.key.integer_id())
    if will_un_public:
      deferred.defer(cls.delete, doc_id)
    else:
      if project.language == "ja":
        queue = "yahoo-japan-jlp-ma"
      else:
        queue = "default"
      text = " ".join((project.name, project.description))
      deferred.defer(cls.put,
                     doc_id, text, project.language,
                     _queue=queue)

  @classmethod
  def put(cls, doc_id, text, language):
    if language == "ja":
      from util import jlp_api
      fields = [search.TextField(name="a", value=word, language=language) for word in jlp_api.ma(text)]
    else:
      fields = [search.TextField(name="a", value=text, language=language)]
    cls.search_index.put(search.Document(
      doc_id = doc_id,
      fields = fields,
    ))

  @classmethod
  def delete(cls, key):
    cls.search_index.delete(key)
