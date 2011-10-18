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

import sys


class State(object):
  pass


class Start(State):
  pass


class End(State):
  pass


class FileEnd(State):
  pass


class InString(State):
  pass


class StringEscape(State):
  pass


class IdentifierState(State):
  pass


class IntOrFloat(State):
  pass


class FloatState(State):
  pass


class TokenType(object):
  pass

class EndOfFile(TokenType):
  short_name = 'fend'


class Identifier(TokenType):
  short_name = 'idnt'


class Integer(TokenType):
  short_name = 'intr'


class Float(TokenType):
  short_name = 'flot'


class String(TokenType):
  short_name = 'strn'


class Character(TokenType):
  short_name = 'char'


class Token(object):

  def __init__(self, token_type=None, value=None):
    self.token_type = token_type
    self.value = value

  def print_node(self, indent):
    pass


class Lexer(object):

  def __init__(self, stream):
    self.stream = stream
    self.current = ''
    self.state = Start

  def next_token(self):
    token = Token(token_type=EndOfFile, value='')

    if self.current == '':
      self.current = self.stream.read(1)

    while self.state != End and self.state != FileEnd:
      if self.current == '' or ord(self.current) == 10:
        if self.state == IntOrFloat:
          token.token_type = Integer
        self.state = FileEnd
        return token
      elif self.state == Start and self.current == '"':
        self.state = InString
        token.token_type = String
        token.value += self.current
        self.current = self.stream.read(1)
      elif self.state == InString and self.current == '"':
        self.state = Start
        token.value += self.current
        self.current = self.stream.read(1)
        return token
      elif self.state == InString and self.current == '\\':
        self.state = StringEscape
        token.value += self.current
        self.current = self.stream.read(1)
      elif self.state == Start and self.current.isdigit():
        self.state = IntOrFloat
        token.value += self.current
        self.current = self.stream.read(1)
      elif self.state == IntOrFloat and self.current == '.':
        self.state = FloatState
        token.token_type = Float
        token.value += self.current
        self.current = self.stream.read(1)
      elif ((self.state == IntOrFloat or self.state == FloatState)
            and not self.current.isdigit()):
        if self.state == IntOrFloat:
          token.token_type = Integer
        self.state = Start
        return token
      elif self.state == Start and self.current.isalpha():
        token.token_type = Identifier
        self.state = IdentifierState
        token.value += self.current
        self.current = self.stream.read(1)
      elif (self.state == IdentifierState and
            (not self.current.isalpha() and not self.current.isdigit()
             and not self.current == '_')):
        self.state = Start
        return token
      elif self.state == Start:
        token.value += self.current
        token.token_type = Character
        self.current = self.stream.read(1)
        return token
      else:
        token.value += self.current
        self.current = self.stream.read(1)

    return token

  def all_tokens(self):
    tokens = []
    token = self.next_token()
    #while token.token_type != EndOfFile:
    tokens.append(token)
    return tokens


class Node(object):
  node_type = None

  def __init__(self, children=None):
    self.children = children or []

  def print_node(self, indent=0):
    for i in xrange(indent):
      print '',
    print self.node_type
    for child in self.children:
      child.print_node(indent + 2)

class Module(Node):
  node_type = 'modl'

  def build(self, tokens):
    while tokens.current() is not None:
      self.children.append(tokens.current())
      tokens.next()
    pass

class Assignment(Node):
  node_type = 'asgn'

class VariableDeclaration(Node):
  node_type = 'vdec'

class ClassDeclaration(Node):
  node_type = 'cdec'

class FunctionDeclaration(Node):
  node_type = 'fdec'

class IfStatemenet(Node):
  node_type = 'ifst'

class ElseClause(Node):
  node_type = 'else'


class TokenIterator(object):

  def __init__(self, token_list):
    self.token_list = token_list
    self.index = 0

  def current(self):
    if self.index < len(self.token_list):
      return self.token_list[self.index]
    else:
      return None

  def next(self):
    self.index += 1
    return self.current()

  def look_ahead(self, steps):
    for i in xrange(steps):
      result = self.next()
    self.index -= steps
    return result
    


def build_tree(tokens):
  m = Module()
  m.build(TokenIterator(tokens))
  return m


if __name__ == '__main__':
  lexer = Lexer(sys.stdin)
  tokens = lexer.all_tokens()
  root = build_tree(tokens)
  root.print_node()
