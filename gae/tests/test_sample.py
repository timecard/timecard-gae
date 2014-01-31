# -*- coding: utf-8 -*-

import tests.util

from google.appengine.api import taskqueue
import endpoints

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
    self.app.post_json(self.endpoints_uri("Me.create"), {
      "name": "me",
      "language": "en",
    })
    response = self.app.post_json(self.endpoints_uri("Me.get"))
    assert response.json == {u'key': u'1C', u'language': u'en', u'name': u'me'}
    response = self.app.post_json(self.endpoints_uri("Me.update"), {
      "name": u"日本語",
      "language": "ja",
    })
    assert response.json == {u'key': u'1C', u'language': u'ja', u'name': u'日本語'}
    response = self.app.post_json(self.endpoints_uri("User.search"), {
      "query": "none",
    })
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("User.list"), {
      "items": [{"key": "none"}],
    })
    assert response.json == {}
    response = self.app.post_json(self.endpoints_uri("User.list"), {
      "items": [{"key": "1C"}],
    })
    assert response.json == {u'items': [{u'key': u'1C', u'language': u'ja', u'name': u'日本語'}]}
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "100",
      "name": "me",
    }, status=400)
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "1C",
      "name": "me",
    }, status=400)
    self.app.post_json(self.endpoints_uri("Me.delete"), {
      "key": "1C",
      "name": u"日本語",
    })
