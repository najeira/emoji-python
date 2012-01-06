# -*- coding: utf-8 -*-

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(
  os.path.abspath(__file__))))

import emoji


class MyTest(object):

  def test_convert_docomo_sjis(self):
    obj = emoji.factory('docomo', 'sjis')
    ret = obj.convert('hello \xF8\x9F world')
    assert 'hello [d1] world' == ret, ret

  def test_convert_ezweb_sjis(self):
    obj = emoji.factory('ezweb', 'sjis')
    ret = obj.convert('hello \xF6\x59 world')
    assert 'hello [e1] world' == ret, ret

  def test_convert_softbank_sjis(self):
    obj = emoji.factory('softbank', 'sjis')
    ret = obj.convert('hello \xF9\x41 world')
    assert 'hello [s1] world' == ret, ret

  def test_convert_docomo_utf8(self):
    obj = emoji.factory('docomo', 'utf-8')
    ret = obj.convert('hello \xEE\x98\xBE world')
    assert 'hello [d1] world' == ret, ret

  def test_convert_ezweb_utf8(self):
    obj = emoji.factory('ezweb', 'utf-8')
    ret = obj.convert('hello \xEE\xBD\x99 world')
    assert 'hello [e1] world' == ret, ret

  def test_convert_softbank_utf8(self):
    obj = emoji.factory('softbank', 'utf-8')
    ret = obj.convert('hello \xEE\x80\x81 world')
    assert 'hello [s1] world' == ret, ret

  def test_convert_ezweb_jis(self):
    obj = emoji.factory('ezweb', 'jis-email')
    ret = obj.convert('hello \x1B\x24\x42\x75\x3A\x1B\x28\x42 world')
    ret = ret.decode('iso2022-jp')
    assert 'hello [e1] world' == ret, ret

  def test_restore_docomo_sjis(self):
    obj = emoji.factory('docomo', 'sjis')
    ret = obj.restore('hello [d1] world')
    assert 'hello \xF8\x9F world' == ret, ret

  def test_restore_ezweb_sjis(self):
    obj = emoji.factory('ezweb', 'sjis')
    ret = obj.restore('hello [e1] world')
    assert 'hello \xF6\x59 world' == ret, ret

  def test_restore_softbank_sjis(self):
    obj = emoji.factory('softbank', 'sjis')
    ret = obj.restore('hello [s1] world')
    assert 'hello \xF9\x41 world' == ret, ret

  def test_restore_docomo_utf8(self):
    obj = emoji.factory('docomo', 'utf-8')
    ret = obj.restore('hello [d1] world')
    assert 'hello \xEE\x98\xBE world' == ret, ret

  def test_restore_ezweb_utf8(self):
    obj = emoji.factory('ezweb', 'utf-8')
    ret = obj.restore('hello [e1] world')
    assert 'hello \xEE\xBD\x99 world' == ret, ret

  def test_restore_softbank_utf8(self):
    obj = emoji.factory('softbank', 'utf-8')
    ret = obj.restore('hello [s1] world')
    assert 'hello \xEE\x80\x81 world' == ret, ret

  def test_restore_ezweb_jis(self):
    obj = emoji.factory('ezweb', 'jis-email')
    ret = obj.restore('hello [e1] world')
    assert 'hello \x1B\x24\x42\x75\x3A\x1B\x28\x42 world' == ret, ret


if __name__ == '__main__':
  obj = MyTest()
  for name in dir(obj):
    if not name.startswith('test_'):
      continue
    method = getattr(obj, name)
    start = time.time()
    for i in xrange(1000):
      method()
    elapsed = time.time() - start
    print '%s: %.3f per 1000 procs.' % (name, elapsed)
