#!/usr/bin/env python

import headspace.low_level.core as low_level

C = 'c'
JAVA = 'Java'
JS = 'JavaScript'
PYTHON = 'Python'
PHP = 'PHP'

class UntranslatableError(Exception):
  pass


class LanguageBlock(object):

  def __init__(self, language, code):
    self.language = language
    self.code = code

  def translate(self, language):
    if language == self.language:
      # Return the literal source code, strip off open and closing quotes.
      return self.code[1:-1]
    else:
      return ''

class VariableDeclaration(object):
  
  def __init__(self, name, var_type=None):
    self.name = name
    self.var_type = var_type

  def translate(self, language):
    if language in (C, JAVA):
      return '%s %s;' % (self.var_type, self.name)
    elif language in (JS, PYTHON, PHP):
      return ''
    else:
      return None

class Assignment(object):

  def __init__(self, name, value):
    self.name = name
    self.value = value

  def translate(self, language):
    if language in (C, JAVA, JS):
      return '%s = %s;' % (self.name, self.value)
    elif language == PYTHON:
      return '%s = %s' % (self.name, self.value)
    elif language == PHP:
      return '$%s = %s;' % (self.name, self.value)
    else:
      return None

class FunctionDeclaration(object):
  
  def __init__(self, name, args, rets):
    """
    Args:
      name: The name of the function as a string.
      rets: List of strings
    """

def translate_string(s, language):
  groups = low_level.parse_string(s)
  return translate_groups(groups, language)

def translate_file(filename, language):
  groups = low_level.parse_file(filename)
  return translate_groups(groups, language)

def add_statement(to_translate, statements, language):
  translated = to_translate.translate(language)
  if translated is None:
    raise UntranslatableError('Could not translate into %s' % language)
  elif translated != '':
    statements.append(translated)
  
def translate_groups(groups, language):
  statements = []
  for group in groups:
    if group.get(1) == 'foreign':
      add_statement(LanguageBlock(group.get(2), group.get(3)), statements, 
                    language)
    elif group.get(1) == 'set':
      add_statement(Assignment(group.get(2), group.get(3)), statements, 
                    language)
    elif group.get(1) == 'var':
      add_statement(VariableDeclaration(group.get(2), group.get(3)), 
                    statements, language)
    else:
      raise UntranslatableError('Can\'t convert %s statement' % group.get(1))
  return '\n'.join(statements)


