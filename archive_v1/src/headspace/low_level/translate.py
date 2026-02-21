#!/usr/bin/env python

import headspace.low_level.core as low_level

C = 'c'
JAVA = 'Java'
JS = 'JavaScript'
PYTHON = 'Python'
PHP = 'PHP'


class Error(Exception):
  pass


class StatementTypeError(Error):
  pass


class Module(object):
  
  def __init__(self, language=None, imports=None, declarations=None,
               statements=None, name=None):
    self.language = language
    self.imports = imports or set()
    self.declarations = declarations or []
    self.statements = statements or []
    self.name = name

  # Not done
  def translate(self):
    for statement in self.statements:
      # Each statement is a group.
      statement_type = statement.info(1)
      if statement_type == 'foreign':
        pass        
  
  # Not done
  def to_output(self):
    output = ''
    # Imports
    for i in imports:
      if self.language == C:
        output += '#include%s;\n' % i
      elif self.language == JAVA:
        output += 'import %s;\n' % i
    # Declarations
    # not done
    # Statements to execute in 'main'
    if language == C:
      output += 'void main() {'
      for statement in self.statements:
        pass
      output += '}'
    elif language == Java:
      output += '  public static void main() {'
      for statement in self.statements:
        pass
      output += '}'
    elif language == JavaScript:
      for statement in self.statements:
        pass
    elif language == Python:
      output += 'if __name__ == \'__main__\':':
      for statement in self.statements:
        pass
       
      
      
      
    pass

  def to_file(self, file):
    pass


class Foreign(object):
  """Code written in another language to be injected."""

  def __init__(self, group):
    self.language = group.info(2).value
    self.statement_type = group.info(3).value
    self.code = group.info(4).value

  def add_to_module(self, module):
    if self.language == module.language:
      if self.statement_type == 'import':
        module.imports.add(self.code[1:-1])
      elif self.statement_type == 'decl':
        module.declarations.append(self.code[1:-1])
      elif self.statement_type == 'run':
        module.statements.append(self.code[1:-1])
      else:
        raise StatementTypeError(
          'The foreign code %s was not one of import, decl, or run,'
          ' but was %s' % (self.code, self.statement_type))


def translate_group(group, module):
  group_type = group.info(1).value
  if group_type == 'foreign':
    foreign = Foreign(group)
    foreign.add_to_module(module)
  else:
    StatementTypeError('Unrecognized statement type: %s' % group_type)


def string_to_module(s, language):
  groups = low_level.parse_string(s)
  module = Module(language=language)
  for group in groups:
    translate_group(group, module)
  return module

    

# From here on down is old code.

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

class Print(object):

  def __init__(self, string):
    """Writes the string out to standard output."""
    self.string = string

  def translate(self, language):
    if language == C:
      return 'printf("%%s", %s);' % self.string
    elif language == JAVA:
      return 'System.out.print(%s);' % self.string
    elif language == PYTHON:
      return 'sys.stdout.write(%s)' % self.string
    elif language == JS:
      return 'document.write(%s);' % self.string
    elif language == PHP:
      return 'print %s;' % self.string
    else:
      return None

class Main(object):

  def __init__(self, group):
    """Wraps the commands in group in a main function."""
    self.group = group

  def translate(self, language):
    lines = ['placeholder']
    print 'group count:', self.group.count
    print 'group members:', self.group.members
    for i in xrange(self.group.count):
      member = self.group.get(i + 1)
      print 'type of member', type(member)
      if isinstance(member, (str, unicode)):
        lines.append(member)
      else:
        lines.append(member.translate(language))
    if language == C:
      lines[0] = 'int main(void) {'
      lines.append('  return 0;')
      lines.append('}')
    elif language == JAVA:
      lines[0] = 'public static void main(String[] args) {'
      lines.append('}')
    elif language == PYTHON:
      lines[0] = 'if __name__ == \'__main__\':'
    elif language in (JS, PHP):
      lines[0] = 'function main() {'
      lines.append('};')
      lines.append('main();')
    return '\n'.join(lines)


#def translate_string(s, language):
#  groups = low_level.parse_string(s)
#  return translate_groups(groups, language)

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
    elif group.get(1) == 'print':
      add_statement(Print(group.get(2)), statements, language)
    elif group.get(1) == 'main':
      add_statement(Main(group.get(2)), statements, language)
    else:
      raise UntranslatableError('Can\'t convert %s statement' % group.get(1))
  return '\n'.join(statements)


