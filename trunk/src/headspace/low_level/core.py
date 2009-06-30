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


class Group(object):
  """A collection of indexed values which may have names.

  Value lookup can be performed by name or by index. All values have an index,
  starting at 1, but a value can also be given a name.
  """

  def __init__(self):
    self.members = {}
    self.count = 0

  def add(self, value, name=None):
    """Appends a value giving it the next numeric index."""
    self.set(self.count + 1, value, name)
    self.count += 1

  def set(self, position, value, name=None):
    """Changes the value at the position."""
    if name is not None:
      if not isinstance(name, (str, unicode)):
        raise IllegalIndexError('name must be a string')
      self.members[name] = value
    if not isinstance(position, int):
      raise IllegalIndexError('index number must be an integer')
    self.members[position] = value

  def getByName(self, name):
    if not isinstance(name, (str, unicode)):
      raise IllegalIndexError('name must be a string')
    if name not in self.members:
      raise LookupFailed(name + 'not in group members')
    return self.members[name]

  def getByIndex(self, num):
    if not isinstance(num, int):
      raise IllegalIndexError('index number must be an integer')
    if num < 1 or num > self.count:
      raise LookupFailed('index %s out of range' % str(num))
    return self.members[num]

  def get(self, key):
    if isinstance(key, (str, unicode)):
      return self.getByName(key)
    return self.getByIndex(key)


class SlottedGroup(Group):
  """Group with predefined slots.

  Example usage would be for a function with a few slots predefined:

    f(a, b, third, forth):

  When invoked:

    f('this is for a', third=12, 'should be b', 4)
  """

  def __init__(self, slots):
    """Defines the slots which allows gets by name when name is not specified.

    Args:
      slots: list of strings for slot names. If the slots contains ['a', 'b']
             and a group is '{1 4}' then self.get('a') will return '1'.
    """
    self.members = {}
    self.count = 0
    self.slots = slots

  def get(self, key):
    if isinstance(key, (str, unicode)):
      # TODO:
      pass
    return self.getByIndex(key)

  def add(self, value, name=None):
    pass
      

def next_group(reader):
  """Reads all tokens nested between [], (), and {}.

  Starts on a [ and ends after a ].

  Args:
    reader: TokenReader from which the group should be read.
  """
  current = reader.ct()
  if current is None:
    return None
  if current not in parse_config.GROUP_START:
    raise SyntaxError(
        'Group should start with [, but instead found' + current)
  group = Group()
  # Move past the opening [ to the first member of the group.
  current = reader.next()
  while current and current not in parse_config.GROUP_END:
    member = next_member(reader)
    if len(member) == 2:
      group.add(name=member[0], value=member[1])
    else:
      group.add(member[0])
    # Calling next_member has advanced past the current member.
    current = reader.ct()
  if current in parse_config.GROUP_END:
    # Consume the closing ]
    reader.next()
    return group
  else:
    raise SyntaxError('Group should end with ], but found' + current)


def next_member(reader):
  """Reads a group member which may have a name alias.

  For example, in [x=1, 2] next_member would return the value-name 
  pair '1', 'x' then the value only '2'

  Returns a tuple of length 1 or 2. If the length is 1, the member is the
  value of the member. If the length is 2, the first is the alias/name and
  the second is the value.
  """
  first = reader.ct()
  if first == '=':
    raise SyntaxError('Member pair cannot start with an = sign.')
  elif first in parse_config.GROUP_START:
    first = next_group(reader)
    return (first,)
  elif first in parse_config.GROUP_END:
    # There was nothing in this group, so return None.
    return (None,)
  # The next character could be an = if this is a name-value pair.
  if reader.next() != '=':
    return (first,)
  # So far we've read name=, so we have a name-value pair.
  value = reader.next()
  if value in parse_config.GROUP_START:
    return (first, next_group(reader))
  elif value in parse_config.GROUP_END:
    raise SyntaxError('Value cannot begin with a ] symbol')
  else:
    # Consume the value, position on the next token.
    reader.next()
    return (first, value)
  

class LowLevelParser(object):

  def __init__(self, tokens):
    self.tokens = tokens

  def next_group():
    pass

  def all_groups(self):
    reader = TokenReader(self.tokens)
    groups = []
    current = next_group(reader)
    while current:
      groups.append(current)
      current = next_group(reader)
    return groups


def parse_string(s):
  parser = LowLevelParser(lex.lex_string(s))
  return parser.all_groups()


def parse_file(filename):
  parser = LowLevelParser(lex.lex_file(filename))
  return parser.all_groups()
