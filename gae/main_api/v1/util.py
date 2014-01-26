# -*- coding: utf-8 -*-

import tap
from pyahooapis import jlp

api = jlp.JLPAPIs("dj0zaiZpPUNoZVZJaUVyTU1KaCZzPWNvbnN1bWVyc2VjcmV0Jng9MGY-")

class jlp_api(object):
  @staticmethod
  def ma(text):
    for word in api.ma.get_result_set(text).ma_result.words:
      if word.pos not in (u"助詞", u"特殊"):
        yield word.surface
