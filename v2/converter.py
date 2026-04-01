import parser
import sys
import os

# Checklist for converting headspace parse trees to target languages:
#   FEATURE NAME                         SUPPORTED LANGUAGES
# - creating main function               c  py  js  go  c#  java
# - converting print statement           c  py  js  go  c#  java
# - passing through foreign code         c  py  js  go  c#  java
# - function declarations                c
# - function calling                     c
# - importing modules

class SourceCodeFile:

  def __init__(self, filename, content):
    self.filename = filename
    self.content = content


def find_module_name(parse_tree):
  module_name = None
  for top_node in parse_tree.members:
    if (top_node.node_type == 'ASSIGNMENT' and
        top_node.members[0].node_type == 'ASSIGNMENT_TARGET' and
        top_node.members[0].members[0] == 'moduleName' and
        top_node.members[2].node_type == 'STRING_LITERAL' and
        top_node.members[2].members[0][0] == '"'):
      module_name = top_node.members[2].members[0][1:-1]
      return module_name
  return module_name


def find_main_function(parse_tree):
  for top_node in parse_tree.members:
    if (top_node.node_type == 'FUNCTION_DECLARATION' and
        top_node.members[0].node_type == 'IDENTIFIER' and
        top_node.members[0].members[0] == 'main'):
      return top_node
  return None


def find_function_return_type(function_declaration_node):
  return function_declaration_node.members[2].members[1].members[0]


def find_function_identifier(function_declaration_node):
  return function_declaration_node.members[0].members[0]


def find_function_parameters(function_declaration_node):
  params = []
  for node in function_declaration_node.members[2].members:
    if node.node_type == 'DECLARATION':
      param_name = node.members[0].members[0]
      param_type = node.members[2].members[0]
      params.append((param_name, param_type))
  return params


def find_function_body_code_block(function_declaration_node):
  for node in function_declaration_node.members[2].members:
    if node.node_type == 'CODE_BLOCK':
      return node
  print('Expected function definition to contain a code block for the body.')
  sys.exit(1)


class ConverterToC:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, c_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        c_code.append(' ' * (indent_level))
        if function_call_node.members[0].members[2].members[0] == 'print':
          c_code.append('printf("%s", ')
        elif function_call_node.members[0].members[2].members[0] == 'printInt':
          c_code.append('printf("%d", ')
        if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
          c_code.append(function_call_node.members[1].members[1].members[0].members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
          for chain_entry in function_call_node.members[1].members[1].members[0].members:
            c_code.append(chain_entry.members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'FUNCTION_CALL'):
          self.emit_function_call(function_call_node.members[1].members[1].members[0], c_code, indent_level)
        c_code.append(');\n')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        # Emit the chain of identifiers.
        for chain_node in function_call_node.members[0].members:
          c_code.append(chain_node.members[0])
        # Emit the arguments for the function call.
        if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
          c_code.append('(')
          first_arg = True
          for argument_node in function_call_node.members[1].members[1].members:
            if not first_arg:
              c_code.append(' ,')
            if argument_node.node_type == 'NUMBER_LITERAL':
              c_code.append(argument_node.members[0])
              first_arg = False
          c_code.append(')')
        else:
          print('Function call was missing a list of arguments.')
          sys.exit(1)

  def emit_foreign_code_block(self, foreign_code_block_node, c_code, indent_level):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == 'C':
      for c_token in foreign_code_block_node.members[0].members:
        c_code.append(c_token)

  def emit_identifier_chain(self, identifier_chain_node, c_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        c_code.append(member.members[0])


  def emit_code_statement(self, statement_node, c_code, indent_level):
    if statement_node.node_type == 'INFIX_OPERATION':
      for sub_node in statement_node.members:
        self.emit_code_statement(sub_node, c_code, indent_level)
    elif statement_node.node_type == 'IDENTIFIER_CHAIN':
      self.emit_identifier_chain(statement_node, c_code, indent_level)
    elif statement_node.node_type == 'OPERATOR':
      c_code.append(' ' + statement_node.members[0] + ' ')


  def emit_return_statement(self, return_statement_node, c_code, indent_level):
    if return_statement_node.members[0]:
      c_code.append(' ' * indent_level)
      c_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], c_code, indent_level)
      c_code.append(';\n')

  def emit_code_block(self, code_block_node, c_code, indent_level):
    c_code.append('\n{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, c_code, indent_level + 2)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, c_code, indent_level + 2)
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, c_code, indent_level + 2)
    c_code.append('}\n')

  def convert_data_type(self, provided_type):
    if provided_type == 'int32':
      return 'int32_t'
    else:
      return provided_type

  def emit_function_signature(self, function_declaration_node, h_code, indent_level):
    # Skip the main function since it is not included in a .h file.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    h_code.append(self.convert_data_type(return_type) + ' ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      h_code.append(self.convert_data_type(function_params[param_index][1]) + ' ' + function_params[param_index][0] + ', ')
      param_index += 1
    h_code.append(self.convert_data_type(function_params[len(function_params) - 1][1]) + ' ' + function_params[len(function_params) - 1][0] + ');\n')

  def emit_function_body(self, function_body_node, c_code, indent_level):
    self.emit_code_block(function_body_node, c_code, indent_level)

  def emit_function_definition(self, function_declaration_node, c_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the c_code.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    c_code.append(self.convert_data_type(return_type) + ' ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      c_code.append(self.convert_data_type(function_params[param_index][1]) + ' ' + function_params[param_index][0] + ', ')
      param_index += 1
    c_code.append(self.convert_data_type(function_params[len(function_params) - 1][1]) + ' ' + function_params[len(function_params) - 1][0] + ')')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), c_code, indent_level)
    c_code.append('\n')

  def emit_code(self):
    c_code = []
    h_code = []
    module_name = find_module_name(self.tree)
    module_name_c = module_name + '.c'
    module_name_h = module_name + '.h'

    # Start the .h file with a ifdef guard.
    h_code.append('#ifndef HEADSPACE_' + module_name.upper() + '_H\n#define HEADSPACE_' + module_name.upper() + '_H\n')
    h_code.append('#include<stdint.h>\n')
    h_code.append('\n')

    # Start the .c file with include directives.
    c_code.append('#include<stdio.h>\n')
    c_code.append('#include<stdint.h>\n')
    c_code.append('#include"' + module_name + '.h"\n')
    # TODO: gather the includes needed to express before source code.
    c_code.append('\n')

    for module_level_member in self.tree.members:
      if module_level_member.node_type == 'FUNCTION_DECLARATION':
        self.emit_function_signature(module_level_member, h_code, 0)
        self.emit_function_definition(module_level_member, c_code, 0)
      # TODO: handle top level variable declarations, class defintions, etc.
    # End the .h file with an ifdef guard.
    h_code.append('\n#endif\n')

    # Add the main function at the end of the .c file.
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      c_code.append('int main(void) ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, c_code, 0)
              # Append a return statement before the closing } in the main
              # function's code block.
              c_code.insert(-1, '  return 0;\n')

    return [SourceCodeFile(module_name_c, ''.join(c_code)), SourceCodeFile(module_name_h, ''.join(h_code))]


class ConverterToPython:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, py_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[2].members[0] == 'print'):
        py_code.append(' ' * (indent_level))
        py_code.append('print')
    if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
      py_code.append('(')
      if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
          function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
        py_code.append(function_call_node.members[1].members[1].members[0].members[0])
      elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
        for chain_entry in function_call_node.members[1].members[1].members[0].members:
          py_code.append(chain_entry.members[0])
      # TODO: only append this special end argument in a print function call.
      py_code.append(', end="")')

  def emit_foreign_code_block(self, foreign_code_block_node, py_code, indent_level):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == 'PYTHON':
      for py_token in foreign_code_block_node.members[0].members:
        py_code.append(py_token)

  def emit_code_block(self, code_block_node, py_code, indent_level):
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, py_code, indent_level + 2)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, py_code, indent_level + 2)
    py_code.append('\n')

  def emit_code(self):
    py_code = []
    module_name = find_module_name(self.tree)
    module_name_py = module_name + '.py'
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      py_code.append('def main():\n')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, py_code, 0)
      py_code.append('\nif __name__ == \'__main__\':\n  main()\n')
    return [SourceCodeFile(module_name_py, ''.join(py_code))]


class ConverterToGo:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, go_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[2].members[0] == 'print'):
        go_code.append('\t' * (indent_level))
        go_code.append('fmt.Print')
    if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
      go_code.append('(')
      if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
          function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
        go_code.append(function_call_node.members[1].members[1].members[0].members[0])
      elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
        for chain_entry in function_call_node.members[1].members[1].members[0].members:
          go_code.append(chain_entry.members[0])
      go_code.append(')')

  def emit_foreign_code_block(self, foreign_code_block_node, go_code, indent_level):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == 'GO':
      for go_token in foreign_code_block_node.members[0].members:
        go_code.append(go_token)

  def emit_code_block(self, code_block_node, go_code, indent_level):
    go_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, go_code, indent_level + 1)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, go_code, indent_level + 1)
    go_code.append('\n')
    if indent_level > 0:
      go_code.append('\t' * indent_level)
    go_code.append('}\n')

  def emit_code(self):
    go_code = []
    module_name = find_module_name(self.tree)
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      go_code.append('package main\n\n')
      go_code.append('import "fmt"\n\n')
      go_code.append('func main() ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, go_code, 0)
      # Create file name with a main.go module.
      main_module_filename = os.path.join(module_name, 'main.go')
      return [SourceCodeFile(main_module_filename, ''.join(go_code))]


class ConverterToJavaScript:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, js_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[2].members[0] == 'print'):
        js_code.append(' ' * (indent_level))
        js_code.append('process.stdout.write')
    if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
      js_code.append('(')
      if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
          function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
        js_code.append(function_call_node.members[1].members[1].members[0].members[0])
      elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
        for chain_entry in function_call_node.members[1].members[1].members[0].members:
          js_code.append(chain_entry.members[0])
      js_code.append(');')

  def emit_foreign_code_block(self, foreign_code_block_node, js_code, indent_level):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == 'JS':
      for js_token in foreign_code_block_node.members[0].members:
        js_code.append(js_token)

  def emit_code_block(self, code_block_node, js_code, indent_level):
    js_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, js_code, indent_level + 2)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, js_code, indent_level + 2)
    js_code.append('\n')
    if indent_level > 0:
      js_code.append(' ' * indent_level)
    js_code.append('}\n')

  def emit_code(self):
    js_code = []
    module_name = find_module_name(self.tree)
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      js_code.append('function main() ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, js_code, 0)
      js_code.append('\nmain();\n')
      module_filename = module_name + '.js'
      return [SourceCodeFile(module_filename, ''.join(js_code))]


class ConverterToJava:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, java_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[2].members[0] == 'print'):
        java_code.append(' ' * (indent_level))
        java_code.append('System.out.print')
    if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
      java_code.append('(')
      if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
          function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
        java_code.append(function_call_node.members[1].members[1].members[0].members[0])
      elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
        for chain_entry in function_call_node.members[1].members[1].members[0].members:
          java_code.append(chain_entry.members[0])
      java_code.append(');')

  def emit_foreign_code_block(self, foreign_code_block_node, java_code, indent_level):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == 'JAVA':
      for java_token in foreign_code_block_node.members[0].members:
        java_code.append(java_token)

  def emit_code_block(self, code_block_node, java_code, indent_level):
    java_code.append('\n')
    if indent_level > 0:
      java_code.append(' ' * indent_level)
    java_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, java_code, indent_level + 2)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, java_code, indent_level + 2)
    java_code.append('\n')
    if indent_level > 0:
      java_code.append(' ' * indent_level)
    java_code.append('}\n')

  def emit_code(self):
    java_code = []
    module_name = find_module_name(self.tree)
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      java_class_name = module_name.capitalize()
      java_code.append('public class ' + java_class_name + '\n')
      java_code.append('{\n')
      java_code.append('  public static void main(String[] args)')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, java_code, 2)
      java_code.append('}\n')
      # Create file name with a .java class file.
      java_class_filename = java_class_name + '.java'
      return [SourceCodeFile(java_class_filename, ''.join(java_code))]


class ConverterToDotNet:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, dotnet_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[2].members[0] == 'print'):
        dotnet_code.append(' ' * (indent_level))
        dotnet_code.append('Console.Write')
    if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
      dotnet_code.append('(')
      if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
          function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
        dotnet_code.append(function_call_node.members[1].members[1].members[0].members[0])
      elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
        for chain_entry in function_call_node.members[1].members[1].members[0].members:
          dotnet_code.append(chain_entry.members[0])
      dotnet_code.append(');')

  def emit_foreign_code_block(self, foreign_code_block_node, dotnet_code, indent_level):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == 'DOTNET':
      for dotnet_token in foreign_code_block_node.members[0].members:
        dotnet_code.append(dotnet_token)

  def emit_code_block(self, code_block_node, dotnet_code, indent_level):
    dotnet_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, dotnet_code, indent_level + 2)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, dotnet_code, indent_level + 2)
    dotnet_code.append('\n')
    if indent_level > 0:
      dotnet_code.append(' ' * indent_level)
    dotnet_code.append('}\n')

  def emit_code(self):
    dotnet_code = []
    module_name = find_module_name(self.tree)
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      dotnet_class_name = module_name.capitalize()
      dotnet_code.append('using System;\n')
      dotnet_code.append('\n')
      dotnet_code.append('namespace ' + dotnet_class_name + ' {\n')
      dotnet_code.append('  class MainProgram {\n')
      dotnet_code.append('    static void Main(string[] args) ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, dotnet_code, 4)
      dotnet_code.append('  }\n')
      dotnet_code.append('}\n')
      # Create file name with a .cs (C#) module.
      dotnet_class_filename = dotnet_class_name + '.cs'
      return [SourceCodeFile(dotnet_class_filename, ''.join(dotnet_code))]


def convert(parse_tree, target_langauge):
  if target_langauge == 'c':
    converter = ConverterToC(parse_tree)
  elif target_langauge == 'python':
    converter = ConverterToPython(parse_tree)
  elif target_langauge == 'go':
    converter = ConverterToGo(parse_tree)
  elif target_langauge == 'javascript':
    converter = ConverterToJavaScript(parse_tree)
  elif target_langauge == 'java':
    converter = ConverterToJava(parse_tree)
  elif target_langauge == 'dotnet':
    converter = ConverterToDotNet(parse_tree)
  else:
    print('invalid language selected for output')
    sys.exit(1)
  return converter.emit_code()

