# -*- coding: utf-8 -*-

import tests.util

from google.appengine.api import taskqueue
from google.appengine.ext import ndb
import endpoints

from main_api.v1 import model
import main_api.v1

class AppTest(tests.util.TestCase):
  application = main_api.v1.api

  def test_me(self):
    self.endpoints_via_oauth(email="me@localhost", _user_id=100)
    self.app.post_json(self.endpoints_uri("Me.get"), status=404)
    self.app.post_json(self.endpoints_uri("Me.update"), status=400)
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "100",
      "name": "me",
    }, status=400)
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "1C",
      "name": "me",
    }, status=404)
    self.app.post_json(self.endpoints_uri("Me.create"), {}, status=400)
    self.app.post_json(self.endpoints_uri("Me.create"), {
      "name": "me",
    })
    response = self.app.post_json(self.endpoints_uri("Me.get"))
    assert response.json == {u'key': u'1C', u'language': u'en', u'name': u'me'}
    response = self.app.post_json(self.endpoints_uri("Me.update"), {
      "name": u"日本語",
    })
    assert response.json == {u'key': u'1C', u'language': u'en', u'name': u'日本語'}
    self.execute_tasks("default")
    response = self.app.post_json(self.endpoints_uri("User.search"), {
      "query": "none",
    })
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("User.search"), {
      "query": u"日本語",
    })
    assert response.json == {u'items': [{u'key': u'1C', u'language': u'en', u'name': u'日本語'}]}
    response = self.app.post_json(self.endpoints_uri("User.list"), {
      "items": [{"key": "none"}],
    })
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("User.list"), {
      "items": [{"key": "1C"}],
    })
    assert response.json == {u'items': [{u'key': u'1C', u'language': u'en', u'name': u'日本語'}]}
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "100",
      "name": "me",
    }, status=400)
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "1C",
      "name": "me",
    }, status=400)
    project = self.app.post_json(self.endpoints_uri("Project.create"), {
      "name": u"日本語",
    }).json
    assert ndb.Key(model.Project, int(project["key"])).get()
    response = self.app.post_json(self.endpoints_uri("Project.list"))
    assert len(response.json["items"]) == 1
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "1C",
      "name": u"日本語",
    }, status=403)
    response = self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "closed": True,
    })
    response = self.app.post_json(self.endpoints_uri("Project.delete"), {
      "key": project["key"],
      "name": project["name"],
    })
    self.execute_tasks("default")
    assert not ndb.Key(model.Project, int(project["key"])).get()
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "1C",
      "name": u"日本語",
    })
    response = self.app.post_json(self.endpoints_uri("User.search"), {
      "query": u"日本語",
    })
    # case: search indexは存在するが、userは居ない
    assert response.json == {}

  def test_project(self):
    self.endpoints_via_oauth(email="me@localhost", _user_id=100)
    self.app.post_json(self.endpoints_uri("Project.create"), status=401)
    response = self.app.post_json(self.endpoints_uri("Project.list"))
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("Project.search"), {
      "query": "test",
    })
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("Me.create"), {
      "name": u"日本語",
      "language": "ja",
    })
    project = self.app.post_json(self.endpoints_uri("Project.create"), {
      "name": "en",
    }).json
    assert project == {u'admin': [u'1C'],
                       u'closed': False,
                       u'description': u'',
                       u'is_public': True,
                       u'key': u'1',
                       u'language': u'ja',
                       u'member': [u'1C'],
                       u'name': u'en'}
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
    }, status=400)
    project = self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "name": u"日本語",
      "language": "en",
      "closed": True,
    }).json
    assert project['name'] == u'\u65e5\u672c\u8a9e'
    response = self.app.post_json(self.endpoints_uri("Project.list"))
    assert len(response.json["items"]) == 1
    self.execute_tasks("default")
    response = self.app.post_json(self.endpoints_uri("Project.search"), {
      "query": u"日本語",
    })
    assert len(response.json["items"]) == 1
    response = self.app.post_json(self.endpoints_uri("Project.delete"), {
      "key": project["key"],
    }, status=400)
    response = self.app.post_json(self.endpoints_uri("Project.delete"), {
      "key": project["key"],
      "name": u"日本語",
    })
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("Project.search"), {
      "query": u"日本語",
    })
    assert response.json == {}

  def test_project_admin(self):
    self.endpoints_via_oauth(email="me@localhost", _user_id=100)
    self.app.post_json(self.endpoints_uri("Me.create"), {
      "name": u"日本語",
    })
    self.endpoints_via_oauth(email="me@localhost", _user_id=200)
    self.app.post_json(self.endpoints_uri("Me.create"), {
      "name": u"日本語",
    })
    project = self.app.post_json(self.endpoints_uri("Project.create"), {
      "name": u"日本語",
    }).json
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "admin": project["admin"] + ["3e"],
    }, status=400)
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "admin": project["admin"] + ["100"],
    }, status=400)
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "admin": project["admin"] + ["100"],
      "member": project["member"] + ["100"],
    }, status=400)
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "admin": project["admin"] + ["3e"],
      "member": project["member"] + ["3e"],
    }, status=400)
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "admin": project["admin"] + ["1C"],
      "member": project["member"] + ["1C"],
    })
    self.app.post_json(self.endpoints_uri("Project.delete"), {
      "key": project["key"],
      "name": u"日本語",
    }, status=400)
    self.app.post_json(self.endpoints_uri("Project.update"), {
      "key": project["key"],
      "closed": True,
    })
    self.app.post_json(self.endpoints_uri("Project.delete"), {
      "key": project["key"],
      "name": u"日本語",
    })
