import parser
import sys
import os

# Checklist for converting headspace parse trees to target languages:
# Converting to C
#   - creating main function - done
#   - converting print statement - done
# Converting to Python
#   - creating main function - done
#   - converting print statement - done
# Converting to Java
# Converting to .NET (C#)
# Converting to Go
#   - creating main function - done
#   - converting print statement - done

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


class ConverterToC:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def emit_function_call(self, function_call_node, c_code):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[2].members[0] == 'print'):
        c_code.append('printf')
    if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
      c_code.append('(')
      if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
          function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
        c_code.append(function_call_node.members[1].members[1].members[0].members[0])
      c_code.append(');')

  def emit_code_block(self, code_block_node, c_code):
    c_code.append('\n{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, c_code)
    c_code.append('\n}\n')

  def emit_code(self):
    c_code = []
    module_name = find_module_name(self.tree)
    module_name_c = module_name + '.c'
    module_name_h = module_name + '.h'
    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      # TODO: gather the includes needed to express before source code.
      c_code.append('#include<stdio.h>\n')
      c_code.append('int main(void) ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, c_code)
              # Append a return statement before the closing } in the main
              # function's code block.
              c_code.insert(-1, 'return 0;\n')
    return [SourceCodeFile(module_name_c, ''.join(c_code)), SourceCodeFile(module_name_h, '')]


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
      # TODO: only append this special end argument in a print function call.
      py_code.append(', end="")')

  def emit_code_block(self, code_block_node, py_code, indent_level):
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, py_code, indent_level + 2)
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
      go_code.append(')')

  def emit_code_block(self, code_block_node, go_code, indent_level):
    go_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, go_code, indent_level + 1)
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


def convert(parse_tree, target_langauge):
  if target_langauge == 'c':
    converter = ConverterToC(parse_tree)
  elif target_langauge == 'python':
    converter = ConverterToPython(parse_tree)
  elif target_langauge == 'go':
    converter = ConverterToGo(parse_tree)
  else:
    print('invalid language selected for output')
    sys.exit(1)
  return converter.emit_code()

