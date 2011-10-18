#!/usr/bin/python

# Copyright 2011 Jeffrey William Scudder
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import parser
import StringIO


class LexerTest(unittest.TestCase):

  def assertNextToken(self, lexer, short_name, value):
    token = lexer.next_token()
    self.assertEquals(token.token_type.short_name, short_name)
    self.assertEquals(token.value, value)

  def test_string(self):
    lexer = parser.Lexer(StringIO.StringIO('"str"'))
    self.assertNextToken(lexer, 'strn', '"str"')

  def test_escaped_string(self):
    lexer = parser.Lexer(StringIO.StringIO('"st\\f"'))
    self.assertNextToken(lexer, 'strn', '"st\\f"')

  def test_escaped_quote(self):
    lexer = parser.Lexer(StringIO.StringIO('"st\\"x"'))
    self.assertNextToken(lexer, 'strn', '"st\\"x"')

  def test_int(self):
    lexer = parser.Lexer(StringIO.StringIO('5'))
    self.assertNextToken(lexer, 'intr', '5')

  def test_float(self):
    lexer = parser.Lexer(StringIO.StringIO('5.1'))
    self.assertNextToken(lexer, 'flot', '5.1')

  def test_ident(self):
    lexer = parser.Lexer(StringIO.StringIO('var'))
    self.assertNextToken(lexer, 'idnt', 'var')

  def test_character(self):
    lexer = parser.Lexer(StringIO.StringIO('['))
    self.assertNextToken(lexer, 'char', '[')

  def test_two_characters(self):
    lexer = parser.Lexer(StringIO.StringIO('[)'))
    self.assertNextToken(lexer, 'char', '[')
    self.assertNextToken(lexer, 'char', ')')

  def test_ident_string(self):
    lexer = parser.Lexer(StringIO.StringIO('var"str"'))
    self.assertNextToken(lexer, 'idnt', 'var')
    self.assertNextToken(lexer, 'strn', '"str"')

  def test_int_ident(self):
    lexer = parser.Lexer(StringIO.StringIO('52xyz'))
    self.assertNextToken(lexer, 'intr', '52')
    self.assertNextToken(lexer, 'idnt', 'xyz')

  def test_ident_char(self):
    lexer = parser.Lexer(StringIO.StringIO('var5*'))
    self.assertNextToken(lexer, 'idnt', 'var5')
    self.assertNextToken(lexer, 'char', '*')
  
  def test_char_ident(self):
    lexer = parser.Lexer(StringIO.StringIO('.x9'))
    self.assertNextToken(lexer, 'char', '.')
    self.assertNextToken(lexer, 'idnt', 'x9')

  def test_char_ident(self):
    lexer = parser.Lexer(StringIO.StringIO('9.1-y'))
    self.assertNextToken(lexer, 'flot', '9.1')
    self.assertNextToken(lexer, 'char', '-')
    self.assertNextToken(lexer, 'idnt', 'y')

  def test_whitespace_ident(self):
    lexer = parser.Lexer(StringIO.StringIO(' y_3'))
    self.assertNextToken(lexer, 'char', ' ')
    self.assertNextToken(lexer, 'idnt', 'y_3')

  def test_use_all_tokens(self):
    lexer = parser.Lexer(StringIO.StringIO(' '))
    self.assertNextToken(lexer, 'char', ' ')
    self.assertNextToken(lexer, 'fend', '')
    self.assertNextToken(lexer, 'fend', '')
    self.assertNextToken(lexer, 'fend', '')
   

     
if __name__ == '__main__':
  unittest.main()
