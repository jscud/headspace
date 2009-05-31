#!/usr/bin/env python


import StringIO
import headspace.parser.parse_config as p


class TokenError(Exception):
  pass


class Lexer(object):

  def __init__(self, input):
    self.input = input
    # The current character read from the file.
    self.c = ''
    # The current token being constructed.
    self.token = ''
    # Tokens which have been read from the input.
    self.tokens = []

  def _next_c(self):
    self.c = self.input.read(1)
    return self.c

  def _next_string(self):
    # The first character should be a STRING_START
    if self.c not in p.STRING_START:
      raise TokenError('String literal did not begin with STRING_START')
    # Begin this token with STRING_START.
    self.token += self.c
    self._next_c()
    while self.c:
      self.token += self.c
      # If this is a closing char and is not escaped, this is end of string.
      if self.c in p.STRING_END and self.token[-2] not in p.ESCAPE_CHAR:
        # Move beyond the closing quote char.
        self._next_c()
        return self.token
      # Read the next character.
      self._next_c()
    return self.token

  def _next_identifier(self):
    while self.c and self.c not in p.STOP_CHARS: 
      self.token += self.c
      # Moves to the next char.
      self._next_c()
    # The current char is either '' or a STOP_CHAR.
    return self.token

  def _next_comment(self):
    # The first character should be a COMMENT_START
    if self.c not in p.COMMENT_START:
      raise TokenError('Comment did not begin with COMMENT_START')
    self.token += self.c
    self._next_c()
    while self.c and self.c not in p.COMMENT_END:
      self.token += self.c
      self._next_c()
    return self.token

  def _next_token(self):
    """Loads the next token from input."""
    # Start with a new current token.
    self.token = ''
    # Load the first character of this token.
    if self.c == '':
      self._next_c()
    # Skip over leading whitespace.
    while self.c in p.WHITESPACE:
      self._next_c()
    if self.c in p.STRING_START:
      return self._next_string()
    if self.c in p.COMMENT_START:
      return self._next_comment()
    elif self.c in p.GET_MEMBER:
      self.token = self.c
      self._next_c()
      return self.token
    elif self.c in p.STOP_CHARS:
      self.token = self.c
      self._next_c()
      return self.token
    else:
      return self._next_identifier()
    return self.token

  def parse_all(self):
    current_token = self._next_token()
    while current_token != '':
      self.tokens.append(current_token)
      current_token = self._next_token()
   
 
def lex_string(s):
  f = StringIO.StringIO(s)
  l = Lexer(f)
  l.parse_all()
  return l.tokens


def lex_file(filename):
  f = open(filename)
  l = Lexer(f)
  l.parse_all()
  f.close()
  return l.tokens
