# -*- coding: utf-8 -*-

from __future__ import with_statement

"""
emoji
http://najeira.blogspot.com/

Copyright 2010 najeira
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Text_Pictogram_Mobile
http://openpear.org/package/Text_Pictogram_Mobile

@package Text_Pictogram_Mobile
@author  Daichi Kamemoto <daikame@gmail.com>
@version 0.1.0 

The MIT License

Copyright (c) 2007 - 2008 Daichi Kamemoto <daikame@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import re
import binascii
import threading

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO

__version__ = '0.2.0'
__author__  = 'najeira@gmail.com'


_lock = threading.RLock()
_converters = {}


def factory(agent, type='sjis'):
  agent = agent and agent.lower() or None
  
  with _lock:
    if agent in ('docomo', 'imode', 'i-mode'):
      key = ('D', type)
      if key not in _converters:
        _converters[key] = Docomo(type=type)
      
    elif agent in ('ezweb', 'au', 'kddi'):
      key = ('E', type)
      if key not in _converters:
        _converters[key] = Ezweb(type=type)
      
    elif agent in ('softbank', 'vodafone', 'disney', 'jphone', 'j-phone'):
      key = ('S', type)
      if key not in _converters:
        _converters[key] = Softbank(type=type)
      
    else:
      key = ('N', type)
      if key not in _converters:
        _converters[key] = Nonmobile(type=type)
  
  return _converters[key]


def _to_str(s):
  if not isinstance(s, basestring):
    s = str(s)
  return s


class Base(object):

  def __init__(self, type='sjis', prefix='[', suffix=']', separater=';',
    img='/emoji/', **kwds):
    """
    
    Args:
      type: sjis, utf-8, jis
    
    """
    
    
    self.prefix = prefix
    self.suffix = suffix
    self.separater = separater
    
    type_map = {
      'sjis': 'sjis', 'shift_jis': 'sjis', 'shift-jis': 'sjis', 
      'jis-email': 'jis-email', 'jis': 'jis-email', 'jis_email': 'jis-email', 
      'iso_2022_jp': 'jis', 'iso-2022-jp': 'jis', 
      'utf8': 'utf-8', 'utf-8': 'utf-8', 'utf_8': 'utf-8', 
      }
    self.type = type_map[type.lower()]
    
    self.intercode_re = re.compile(
      re.escape(self.prefix) + r'([des][des\d,]+?)' + re.escape(self.suffix),
      re.S | re.M)
    
    self.img_path = img
    if not self.img_path.endswith('/'):
      self.img_path += '/'
    
    self.number_to_code = {}
    self.code_to_number = {}
    self.converts = {}
    
    self.load_pictograms(self.carrier)
    self.load_converts(self.carrier)

  def get_formatted_pictograms_array(self, carrier):
    # convert hex string to binary string
    binaries = {}
    if carrier == self.carrier:
      for k, v in self.number_to_code[carrier].iteritems():
        binaries[k] = binascii.a2b_hex(v)
    else:
      self.load_converts(carrier)
      for k, v in self.converts[carrier].iteritems():
        binaries[k] = self.get_pictogram(v[self.carrier])
    return binaries

  def get_pictogram(self, number):
    """Returns binary string of argument number.
    If argument number is not numeric, returns argument value.
    """
    number = _to_str(number)
    if number.isdigit():
      unpacked = self.get_pictogram_hex(number)
      return self.to_binary(unpacked)
    elif 0 <= number.find(self.separater):
      numbers = number.split(self.separater)
      unpacked = []
      for number in numbers:
        unpacked.append(self.get_pictogram_hex(number))
      return self.to_binary(''.join(unpacked))
    else:
      #TODO: check and convert encoding?
      return number

  def get_pictogram_hex(self, number):
    """Returns pictogram hex string."""
    return self.number_to_code.get(self.carrier, {}).get(_to_str(number), '')

  def get_pictogram_number(self, char):
    """Returns pictogram number."""
    return self.code_to_number.get(self.carrier, {}).get(char, None)

  def load_pictograms(self, carrier):
    """Loads pictograms information."""
    with _lock:
      if carrier in self.number_to_code and self.number_to_code[carrier]:
        return
      data = getattr(__import__(
        'emoji.data.%s' % carrier, None, None, ['DATA']), 'DATA')[carrier]
      self.number_to_code[carrier] = {}
      self.code_to_number[carrier] = {}
      for k, v in data.iteritems():
        x = v[self.type]
        self.number_to_code[carrier][k] = x
        self.code_to_number[carrier][x] = k

  def load_converts(self, carrier):
    """Loads emoji convertion table."""
    with _lock:
      if carrier in self.converts and self.converts[carrier]:
        return
      self.converts[carrier] = getattr(__import__(
        'emoji.convert.%s' % carrier, None, None, ['DATA']), 'DATA')[carrier]

  def to_intercode(self, char):
    """Converts binary string to emoji intercode."""
    return self.to_intercode_unpacked(binascii.b2a_hex(char))

  def to_intercode_unpacked(self, char):
    """Converts hex string to emoji intercode."""
    if self.is_pictogram_unpacked(char):
      return self.to_intercode_number(self.get_pictogram_number(char))
    return binascii.a2b_hex(char)

  def to_intercode_number(self, number):
    return self.prefix + self.carrier[:1] + _to_str(number) + self.suffix

  def to_binary(self, char):
    """Converts hex string to binary string."""
    if 'jis-email' == self.type:
      char = '1B2442' + char + '1B2842'
    return binascii.a2b_hex(char)

  def is_pictogram(self, char):
    """Returns whether string is pictogram or not."""
    return self.is_pictogram_unpacked(binascii.b2a_hex(char))

  def is_pictogram_unpacked(self, char, carrier=None):
    """Returns whether hex string is pictogram or not."""
    return char in self.code_to_number[carrier or self.carrier]

  def get_numbers_of_intercode(self, intercode):
    alias = {'d': 'docomo', 'e': 'ezweb', 's': 'softbank'}
    numbers = {}
    for elem in intercode.split(','):
      if 2 > len(elem):
        continue
      c = elem[:1]
      if c not in alias:
        continue
      pic = elem[1:]
      if not pic.isdigit():
        continue
      numbers[alias[c]] = pic
    return numbers

  def get_pictogram_from_intercode(self, intercode):
    """Returns pictogram hex string from intercode."""
    numbers = self.get_numbers_of_intercode(intercode)
    if 0 >= len(numbers):
      return None
    # use same carrier number if it exists
    if self.carrier in numbers:
      return self.get_pictogram(numbers[self.carrier])
    # convert number to self carrier
    for from_carrier, from_number in numbers.items():
      self.load_converts(from_carrier)
      to_number = self.converts.get(from_carrier, {}).get(from_number, {}).get(self.carrier)
      if to_number and to_number.isdigit():
        return self.get_pictogram(to_number)
    return intercode

  def _convert(self, text, method):
    if not text:
      return text
    
    text = binascii.b2a_hex(text).upper()
    if 'utf-8' == self.type:
      return self._convert_utf8(text, method)
    elif 'jis-email' == self.type:
      return self._convert_jis(text, method)
    return self._convert_sjis(text, method)

  def _convert_sjis(self, text, method):
    
    output = StringIO()
    
    idx = 0
    last = 0
    while idx < len(text):
      
      nex = text[idx:idx + 2]
      idx += 2
      if idx >= len(text):
        break
      
      #1バイト目がマルチバイトの範囲でなければ次へ
      he = int(nex, 16)
      if 0x00 <= he <= 0x7F or 0xA1 <= he <= 0xDF:
        continue
      
      #2バイト目も取って絵文字なら変換して出力
      nex += text[idx:idx + 2]
      idx += 2
      bin = self.get_pictogram_number(nex)
      if bin:
        
        #絵文字の前までを出力
        pos = idx - 4
        if pos > last:
          output.write(binascii.a2b_hex(text[last:pos]))
        
        #絵文字を変換して出力
        output.write(method(bin))
        
        last = idx
    
    if last < len(text):
      output.write(binascii.a2b_hex(text[last:]))
    
    return output.getvalue()

  def _convert_utf8(self, text, method):
    
    FLAGS = ('EF', 'EE')
    
    output = StringIO()
    
    idx = 0
    last = 0
    while idx < len(text):
      
      nex = text[idx:idx + 2]
      idx += 2
      if idx >= len(text):
        break
      
      #1バイト目が日本語の範囲でなければ次へ
      if nex not in FLAGS:
        continue
      
      #2バイト目と3バイト目も取って絵文字なら返す
      nex += text[idx:idx + 2]
      idx += 2
      if idx >= len(text):
        break
      nex += text[idx:idx + 2]
      idx += 2
      
      bin = self.get_pictogram_number(nex)
      if bin:
        
        #絵文字の前までを出力
        pos = idx - 6
        if pos > last:
          output.write(binascii.a2b_hex(text[last:pos]))
        
        #絵文字を変換して出力
        output.write(method(bin))
        
        last = idx
    
    if last < len(text):
      output.write(binascii.a2b_hex(text[last:]))
    
    return output.getvalue()

  def _convert_jis(self, text, method):
    
    output = StringIO()
    
    idx = 0
    last = 0
    is_mb = False
    while idx < len(text):
      
      #マルチバイトでない間は次へ
      if not is_mb:
        nex = text[idx:idx + 2]
        idx += 2
        if idx >= len(text):
          break
        if '1B' != nex:
          continue
        
        nex = text[idx:idx + 2]
        idx += 2
        if idx >= len(text):
          break
        if '24' != nex:
          continue
        
        nex = text[idx:idx + 2]
        idx += 2
        if idx >= len(text):
          break
        if '42' != nex:
          continue
        
        is_mb = True
      
      #マルチバイトが終了したら次へ
      if idx + 6 < len(text) and '1B2842' == text[idx:idx + 6]:
        idx += 6
        is_mb = False
        continue
      
      #1バイト目と2バイト目を取って絵文字なら返す
      nex = text[idx:idx + 2]
      idx += 2
      if idx >= len(text):
        break
      nex += text[idx:idx + 2]
      idx += 2
      
      bin = self.get_pictogram_number(nex)
      if bin:
        
        #絵文字の前までを出力
        pos = idx - 4
        if pos > last:
          output.write(binascii.a2b_hex(text[last:pos]))
        
        #絵文字を変換して出力
        output.write('\x1B\x28\x42')
        output.write(method(bin))
        output.write('\x1B\x24\x42')
        
        last = idx
    
    if last < len(text):
      output.write(binascii.a2b_hex(text[last:]))
    
    return output.getvalue()

  def convert(self, text):
    return self._convert(text, self.to_intercode_number)

  def replace(self, text):
    return self._convert(text, self._replace)

  def _replace(self, data):
    """Returns binary string that converted from argument."""
    for carrier in ('docomo', 'ezweb', 'softbank'):
      self.load_pictograms(carrier)
      if not self.is_pictogram_unpacked(data, carrier):
        continue
      
      if carrier == self.carrier:
        return data
      
      from_number = self.code_to_number.get(carrier, {}).get(data)
      if not from_number:
        continue
      
      self.load_converts(carrier)
      to_number = self.converts.get(carrier, {}).get(from_number).get(self.carrier)
      return self.number_to_code.get(carrier, {}).get(to_number, data)
      
    return data

  def erase(self, text):
    return self._convert(text, self._erase)

  def _erase(self, data):
    return ''

  def restore(self, text):
    """Returns binary string include emoji.
    It converted from string include intercode emoji
    """
    #TODO: sppedup!
    if 0 >= len(text):
      return text
    matches = self.intercode_re.findall(text)
    replaces = {}
    for matche in matches:
      number = matche if isinstance(matche, basestring) else matche[0]
      emoji = self.get_pictogram_from_intercode(number)
      if emoji:
        replaces[self.prefix + number + self.suffix] = emoji
    for k, v in replaces.iteritems():
      text = text.replace(k, v)
    return text


class Docomo(Base):
  def __init__(self, **kwds):
    self.carrier = 'docomo'
    super(Docomo, self).__init__(**kwds)


class Ezweb(Base):
  def __init__(self, **kwds):
    self.carrier = 'ezweb'
    super(Ezweb, self).__init__(**kwds)


class Softbank(Base):
  def __init__(self, **kwds):
    self.carrier = 'softbank'
    super(Softbank, self).__init__(**kwds)


class Nonmobile(Base):
  def __init__(self, **kwds):
    self.carrier = 'docomo'
    super(Nonmobile, self).__init__(**kwds)

  def get_formatted_pictograms_array(self, carrier):
    return {}

  def get_pictogram(self, number):
    raise NotImplementedError()

  def get_pictogram_hex(self, number):
    raise NotImplementedError()

  def get_pictogram_number(self, char):
    raise NotImplementedError()

  def load_pictograms(self, carrier):
    pass

  def to_intercode(self, char):
    raise NotImplementedError()

  def to_intercode_unpacked(self, char):
    raise NotImplementedError()

  def is_pictogram(self, char):
    raise NotImplementedError()

  def is_pictogram_unpacked(self, char, carrier=None):
    raise NotImplementedError()

  def convert(self, text):
    return text

  def replace(self, text):
    return text

  def get_pictogram_from_intercode(self, intercode):
    """Returns pictogram string from intercode."""
    
    numbers = self.get_numbers_of_intercode(intercode)
    if 0 >= len(numbers):
      return None
    
    # convert number to self carrier
    to_number = None
    to_carrier = None
    for from_carrier, from_number in numbers.items():
      self.load_converts(from_carrier)
      if 'docomo' == from_carrier:
        carriers = ('docomo', 'ezweb', 'softbank')
      else:
        carriers = ('ezweb', 'docomo', 'softbank')
      for x in carriers:
        to_number = self.converts.get(
          from_carrier, {}).get(from_number, {}).get(x)
        if to_number and to_number.isdigit():
          to_carrier = x
          break
    
    if not to_carrier:
      return intercode
    
    if 'docomo' == to_carrier:
      size = 12
    else:
      size = 15
    return '<img src="%s/%s.gif" alt="" border="0" width="%s" height="%s" />' % (
      self.img_path + to_carrier, to_number, size, size)
