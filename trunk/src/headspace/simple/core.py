#!/usr/bin/env python

import headspace.parser.lex as lex
import headspace.parser.parse_config as parse_config


class SyntaxError(Exception):
  pass


class IllegalIndexError(Exception):
  pass


class LookupFailed(Exception):
  pass


class TokenReader(object):

  def __init__(self, tokens):
    self.tokens = tokens
    self.index = 0

  def ct(self):
    """Returns the current token."""
    if self.index < len(self.tokens):
      return self.tokens[self.index]
    return None

  def next(self):
    self.index += 1
    if self.index < len(self.tokens):
      return self.tokens[self.index]
    return None


class FunctionCall(object):

  def __init__(self, name_chain, members):
    self.name_chain = name_chain
    self.members = members


class Identifier(object):

  def __init__(self, name_chain):
    self.name_chain = name_chain


class LiteralString(object):

  def __init__(self, value):
    self.value = value


class LiteralNumber(object):

  def __init__(self, value):
    self.value = value


class Group(object):

  def __init__(self, members):
    self.members = members


def next_item(reader):
  # I wrote this function first.
  if reader.ct() is None:
    return None
  elif reader.ct() == '(':
    return next_group(reader)
  else:
    start = reader.ct()
    if start.startswith('\''):
      reader.next()
      return LiteralString(start)
    elif start[0] in [str(x) for x in xrange(10)]: # TODO: fix logic, use is-digit
      reader.next()
      return LiteralNumber(start)
    else:
      return next_identifier_or_function(reader)


def next_identifier_or_function(reader):
  # I wrote the parsing for an identifier second.
  chain = []
  # First token should be a variable name.
  # TODO: test for a variable name.
  if reader.ct() != '/':
    chain.append(reader.ct())
    reader.next()
  while reader.ct() == '/':
    reader.next()
    if reader.ct() is None:
      raise SyntaxError('Incomplete variable name, ends with /')
    elif reader.ct() == '/':
      raise SyntaxError('Invalid variable name, 2 /s in a row.') 
    elif reader.ct() == '(' or reader.ct() == ')':
      raise SyntaxError('Cannot start a group in a variabe name.')
    elif reader.ct().startswith('\''):
      raise SyntaxError('Variable names cannont contain a string.')
    else:
      chain.append(reader.ct())
      reader.next()
  if reader.ct() == '(':
    # Fourth, I wrote parse rules for a function call.
    argument_group = next_group(reader)
    return FunctionCall(chain, argument_group.members)
  else:
    return Identifier(chain)


def next_group(reader):
  # I wrote parsing for a group third.
  members = {}
  if reader.ct() != '(':
    raise SyntaxError('Group must start with a (, but found %s' % reader.ct())
  reader.next()
  while reader.ct() != ')':
    if reader.ct() is None:
      raise SyntaxError('Unclosed group at the end.')
    key = next_item(reader)
    if not isinstance(key, LiteralNumber) and not isinstance(key, Identifier):
      raise SyntaxError('Group key must be a number or varible name not %s (%s)' % (
                        type(key), key))
    if reader.ct() != '=':
      raise SyntaxError('Group keys and values must be seperated with =.')
    reader.next()
    if reader.ct() is None:
      raise SyntaxError('Group ended with an =.')
    value = next_item(reader)
    if value is None:
      raise SyntaxError('Value in group should not be null.')
    if isinstance(key, LiteralNumber):
      if key.value in members:
        raise SyntaxError('Group already has a value for %s' % key.value)
      members[key.value] = value
    elif isinstance(key, Identifier):
      if len(key.name_chain) != 1:
        raise SyntaxError('Key name can only be a single, unchained identifier.')
      if key.name_chain[0] in members:
        raise SyntaxError('Group already has a value for %s' % key.name_chain[0])
      members[key.name_chain[0]] = value
  # Consume the closing )
  reader.next()
  return Group(members)


def parse_string(s):
  reader = TokenReader(lex.lex_string(s))
  items = []
  current = next_item(reader)
  while current is not None:
    items.append(current)
    current = next_item(reader)
  return items
 
