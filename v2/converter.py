import parser
import sys

# Checklist for converting headspace parse trees to target languages:
# Converting to C
#   - creating main function
#   - converting print statement
# Converting to Python
# Converting to Java
# Converting to .NET (C#)
# Converting to Go

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


class ConverterToC:

  def __init__(self, parse_tree):
    self.tree = parse_tree

  def find_main_function(self):
    for top_node in self.tree.members:
      if (top_node.node_type == 'FUNCTION_DECLARATION' and
          top_node.members[0].node_type == 'IDENTIFIER' and
          top_node.members[0].members[0] == 'main'):
        return top_node
    return None

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
    main_function_declaration = self.find_main_function()
    if main_function_declaration:
      c_code.append('#include<stdio.h>\n')
      #c_code.append('int main(int argc, char** argv) ')
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


def convert(parse_tree, target_langauge):
  if target_langauge == 'c':
    converter = ConverterToC(parse_tree)
  else:
    print('invalid language selected for output')
    sys.exit(1)
  return converter.emit_code()

