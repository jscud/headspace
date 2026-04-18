import parser
import sys
import os

# Checklist for converting headspace parse trees to target languages:
#   FEATURE NAME                         SUPPORTED LANGUAGES
# - creating main function               c  py  go  js  java  c#
# - print statement                      c  py  go  js  java  c#
# - passing through foreign code         c  py  go  js  java  c#
# - function declarations                c  py  go  js  java  c#
# - function calling                     c  py  go  js  java  c#
# - conditional execution (ifs)          c  py  go  js  java  c#
# - declaring variables                  c  py  go  js  java  c#
# - infix and postfix operators          c  py  go  js  java  c#
# - loops (while)                        c  py  go  js  java  c#
# - pass through comments
# - importing modules                    c  py  go  js  java  c#
# - declaring classes
# - allocation memory
# - passing references
# - raising exceptions/errors
#
# Future languages to support:
# C++, Rust, PHP, Ruby


DOTNET_CSPROJ_CONFIG = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>
"""


class SourceCodeFile:

  def __init__(self, filename, content):
    self.filename = filename
    self.content = content


class SymbolTable:

  def __init__(self):
    self.parent_table = None
    self.symbols = {}

  def find_symbol(self, name):
    if name in self.symbols:
      return self.symbols[name]
    elif self.parent_table:
      return self.parent_table.find_symbol(name)

  def set_symbol(self, name, symbol_type):
    self.symbols[name] = symbol_type


class ModuleDetails:

  def __init__(self):
    self.domain_full = None
    self.domain_prefix = None
    self.package_name_parts = None
    self.module_name = None

  def load_from_headspace_source(self, headspace_module_name):
    segments = headspace_module_name.strip('"').split('/')
    if len(segments) < 3:
      print('A moduleName must be in the form "domainName.tld/package/module".')
      sys.exit(1)
    self.domain_full = segments[0]
    self.domain_prefix = self.domain_full.split('.')[0]
    self.package_name_parts = segments[1:-1]
    self.module_name = segments[-1]

  def print(self):
    print('ModuleName:')
    print('  domain_full:', self.domain_full)
    print('  domain_prefix:', self.domain_prefix)
    print('  package_name_parts:', os.path.join(*self.package_name_parts))
    print('  module_name:', self.module_name)

  def to_import(self, target_language):
    #if target_language == 'c':
    return ''

  def to_namespace(self, target_language):
    if target_language == 'c':
      namespace_segments = self.package_name_parts.copy()
      namespace_segments.append(self.module_name)
      return '_'.join(namespace_segments)
    elif target_language == 'go':
      # This is used for the go package name.
      return (''.join(self.package_name_parts)).lower()
    elif target_language == 'java':
      java_path_parts = self.domain_full.split('.')
      java_path_parts.reverse()
      java_path_parts.extend(self.package_name_parts)
      return '.'.join(java_path_parts)
    elif target_language == 'dotnet':
      capitalized_package_name_parts = [name.capitalize() for name in self.package_name_parts]
      return '.'.join(capitalized_package_name_parts)
    return ''

  def to_file_path(self, target_language):
    # Note for C that we avoid adding the .c or .h suffix.
    if target_language == 'c' or target_language == 'python':
      return os.path.join(*self.package_name_parts, self.module_name)
    elif target_language == 'java':
      java_path_parts = self.domain_full.split('.')
      java_path_parts.reverse()
      java_path_parts.extend(self.package_name_parts)
      return os.path.join(*java_path_parts)
    elif target_language == 'dotnet':
      return self.to_namespace(target_language)
    return ''


def parse_module_id(module_id):
  module_details = ModuleDetails()
  module_details.load_from_headspace_source(module_id)
  return module_details


def find_main_function(parse_tree):
  for top_node in parse_tree.members:
    if (top_node.node_type == 'FUNCTION_DECLARATION' and
        top_node.members[0].node_type == 'IDENTIFIER' and
        top_node.members[0].members[0] == 'main'):
      return top_node
  return None


def convert_module_to_language_import(module_details, target_language):
  module_path = module_details.to_file_path(target_language)
  if target_language == 'c':
    return module_path + '.h'
  elif target_language == 'python':
    return '.'.join(module_path.split('/'))
  elif target_language == 'go':
    return module_details.to_namespace('go')
  elif target_language == 'javascript':
    return module_details.module_name
  elif target_language == 'java':
    return '.'.join(module_details.to_file_path('java').split('/')) + '.' + module_details.module_name.capitalize()
  elif target_language == 'dotnet':
    return module_details.to_namespace('dotnet')
  else:
    return module_path


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


def capitalize_first_letter(input_str):
  return input_str[0].capitalize() + input_str[1:]


class HeadspaceConverter:

  #TODO: add a symbol table
  # For the C converter, the module name needs to become a prefix
  # When a library method is called, it needs to be changed from lib.func to lib_func for C.

  def __init__(self, parse_tree):
    self.tree = parse_tree
    self.symbol_table = SymbolTable()
    self.module_details = None

  def emit_foreign_code_block(self, foreign_code_block_node, source_code, target_language):
    if foreign_code_block_node.members[0] and foreign_code_block_node.members[0].node_type == target_language:
      for source_token in foreign_code_block_node.members[0].members:
        source_code.append(source_token)

  def convert_operator(self, provided_operator):
    # For most lanauges, the operator passes through unchanged.
    return provided_operator

  def emit_code_statement(self, statement_node, source_code, indent_level):
    # TODO: Does this need to indent?
    if statement_node.node_type == 'INFIX_OPERATION':
      for sub_node in statement_node.members:
        self.emit_code_statement(sub_node, source_code, indent_level)
    elif statement_node.node_type == 'POSTFIX_OPERATION':
      for sub_node in statement_node.members:
        self.emit_code_statement(sub_node, source_code, indent_level)
    elif statement_node.node_type == 'IDENTIFIER_CHAIN':
      self.emit_identifier_chain(statement_node, source_code, indent_level)
    elif statement_node.node_type == 'OPERATOR':
      if statement_node.members[0] == '++' or statement_node.members[0] == '--':
        source_code.append(self.convert_operator(statement_node.members[0]))
      else:
        source_code.append(' ' + self.convert_operator(statement_node.members[0]) + ' ')
    elif statement_node.node_type == 'NUMBER_LITERAL' or statement_node.node_type == 'STRING_LITERAL':
      source_code.append(statement_node.members[0])

  def emit_condition_expression(self, condition_expression, source_code, indent_level):
    self.emit_code_statement(condition_expression.members[1], source_code, 0)

  def find_imports(self):
    imports = []
    for top_node in self.tree.members:
      if (top_node.node_type == 'IMPORT_STATEMENT' and
          top_node.members[1].node_type == 'MODULE_LOCATION'):
        imported_module_details = parse_module_id(top_node.members[1].members[0].strip('"'))
        module_alias = top_node.members[3].members[0]
        self.symbol_table.set_symbol(module_alias, imported_module_details)
        imports.append(module_alias)
    return imports

  def find_module_details(self):
    for top_node in self.tree.members:
      if (top_node.node_type == 'ASSIGNMENT' and
          top_node.members[0].node_type == 'ASSIGNMENT_TARGET' and
          top_node.members[0].members[0] == 'moduleName' and
          top_node.members[2].node_type == 'STRING_LITERAL' and
          top_node.members[2].members[0][0] == '"'):
        self.module_details = parse_module_id(top_node.members[2].members[0][1:-1])
        #self.module_name = top_node.members[2].members[0][1:-1]
        return self.module_details
    # The module name is required, so we know what to name the output files.
    if not self.module_details:
      print('Headspace source code must specify a module name.')
      sys.exit(1)
    return self.module_details

  def populate_symbol_table_from_declarations(self, top_node):
    for member in top_node.members:
      if member.node_type == 'FUNCTION_DECLARATION':
        function_declaration_node = member
        if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] != 'main':
          self.symbol_table.set_symbol(find_function_identifier(function_declaration_node), 'FUNCTION')


class ConverterToC(HeadspaceConverter):

  def __init__(self, parse_tree):
    super().__init__(parse_tree)

  def emit_function_call(self, function_call_node, c_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or
           function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        c_code.append(' ' * indent_level)
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
          self.emit_function_call(function_call_node.members[1].members[1].members[0], c_code, 0)
        c_code.append(')')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        c_code.append(' ' * indent_level)
        # Emit the chain of identifiers.
        skip_next_dot = False
        for chain_node in function_call_node.members[0].members:
          symbol_for_name = self.symbol_table.find_symbol(chain_node.members[0])
          if symbol_for_name == 'FUNCTION':
            # This is a local function it needs the module name as a prefix.
            c_code.append(self.module_details.module_name + '_' + chain_node.members[0])
          elif type(symbol_for_name) == ModuleDetails:
            # The first member in the chain is a module, so switch to a module_function style call.
            c_code.append(chain_node.members[0])
            # We should use moduleName_functionName instead of parent.functionName since this is a module.
            skip_next_dot = True
          elif chain_node.members[0] == '.' and skip_next_dot:
            c_code.append('_')
            skip_next_dot = False
          else:
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

  def emit_identifier_chain(self, identifier_chain_node, c_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        c_code.append(member.members[0])

  def emit_return_statement(self, return_statement_node, c_code, indent_level):
    if return_statement_node.members[0]:
      c_code.append(' ' * indent_level)
      c_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], c_code, indent_level)
      c_code.append(';\n')

  def convert_data_type(self, provided_type):
    if provided_type == 'int32':
      return 'int32_t'
    else:
      return provided_type

  def emit_variable_declaration(self, variable_declaration, c_code, indent_level):
    c_code.append(' ' * indent_level)
    c_code.append(self.convert_data_type(variable_declaration.members[2].members[0]) + ' ' + variable_declaration.members[0].members[0] + ';\n')

  def emit_assignment_statement(self, assignment_statement, c_code, indent_level):
    c_code.append(' ' * indent_level)
    # TODO: Need to introduce lvalue to be able to assign to things like function call return value.
    if assignment_statement.members[0].node_type == 'ASSIGNMENT_TARGET':
      c_code.append(assignment_statement.members[0].members[0])
    c_code.append(' = ')
    self.emit_code_statement(assignment_statement.members[2], c_code, 0)
    c_code.append(';\n')

  def emit_if_statement(self, if_statement, c_code, indent_level):
    c_code.append(' ' * indent_level)
    c_code.append('if(')
    if if_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(if_statement.members[1], c_code, indent_level)
    c_code.append(')')
    self.emit_code_block(if_statement.members[2], c_code, indent_level)
    if len(if_statement.members) > 4 and if_statement.members[3].node_type == 'ELSE_KEYWORD':
      c_code.append(' ' * indent_level)
      c_code.append('else')
      self.emit_code_block(if_statement.members[4], c_code, indent_level)

  def emit_while_statement(self, while_statement, c_code, indent_level):
    c_code.append(' ' * indent_level)
    c_code.append('while(')
    if while_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(while_statement.members[1], c_code, indent_level)
    c_code.append(')')
    self.emit_code_block(while_statement.members[2], c_code, indent_level)

  def emit_code_block(self, code_block_node, c_code, indent_level):
    c_code.append('\n')
    c_code.append(' ' * indent_level)
    c_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, c_code, indent_level + 2)
        c_code.append(';\n')
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, c_code, 'C')
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, c_code, indent_level + 2)
      elif member.node_type == 'DECLARATION':
        self.emit_variable_declaration(member, c_code, indent_level + 2)
      elif member.node_type == 'ASSIGNMENT':
        self.emit_assignment_statement(member, c_code, indent_level + 2)
      elif member.node_type == 'IF_STATEMENT':
        self.emit_if_statement(member, c_code, indent_level + 2)
      elif member.node_type == 'WHILE_STATEMENT':
        self.emit_while_statement(member, c_code, indent_level + 2)
      elif member.node_type == 'POSTFIX_OPERATION':
        c_code.append(' ' * (indent_level + 2))
        self.emit_code_statement(member, c_code, 0)
        c_code.append(';\n')
    c_code.append(' ' * indent_level)
    c_code.append('}\n')

  def emit_function_signature(self, function_declaration_node, h_code, indent_level):
    # Skip the main function since it is not included in a .h file.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    # For C functions, we use the module name as a prefix to make collisions less likely.
    function_name = self.module_details.module_name + '_' + find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    h_code.append(self.convert_data_type(return_type) + ' ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      h_code.append(self.convert_data_type(function_params[param_index][1]) + ' ' + function_params[param_index][0] + ', ')
      param_index += 1
    if len(function_params) > 0:
      h_code.append(self.convert_data_type(function_params[len(function_params) - 1][1]) + ' ' + function_params[len(function_params) - 1][0])
    elif len(function_params) == 0:
      h_code.append('void')
    h_code.append(');\n')

  def emit_function_body(self, function_body_node, c_code, indent_level):
    self.emit_code_block(function_body_node, c_code, indent_level)

  def emit_function_definition(self, function_declaration_node, c_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the c_code.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = self.module_details.module_name + '_' + find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    c_code.append(' ' * indent_level)
    c_code.append(self.convert_data_type(return_type) + ' ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      c_code.append(self.convert_data_type(function_params[param_index][1]) + ' ' + function_params[param_index][0] + ', ')
      param_index += 1
    if len(function_params) > 0:
      c_code.append(self.convert_data_type(function_params[len(function_params) - 1][1]) + ' ' + function_params[len(function_params) - 1][0])
    elif len(function_params) == 0:
      c_code.append('void')
    c_code.append(')')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), c_code, indent_level)
    c_code.append('\n')

  def emit_code(self):
    c_code = []
    h_code = []
    module_details = self.find_module_details()
    module_path_c = module_details.to_file_path('c') + '.c'
    module_path_h = module_details.to_file_path('c') + '.h'

    includes = []
    for module in self.find_imports():
      # Look for the module name in the symbol table to find details of the module that was imported.
      include_module_details = self.symbol_table.find_symbol(module)
      includes.append('#include"' + convert_module_to_language_import(include_module_details, 'c') + '"\n')

    # Start the .h file with a ifdef guard.
    #h_code.append('#ifndef HEADSPACE_' + module_name.upper() + '_H\n#define HEADSPACE_' + module_name.upper() + '_H\n')
    h_code.append('#ifndef HEADSPACE_' + module_details.to_namespace('c').upper() + '_H\n#define HEADSPACE_' + module_details.to_namespace('c').upper() + '_H\n')
    h_code.append('#include<stdint.h>\n')
    for include in includes:
      h_code.append(include)
    h_code.append('\n')

    # Start the .c file with include directives.
    c_code.append('#include<stdio.h>\n')
    c_code.append('#include<stdint.h>\n')
    for include in includes:
      c_code.append(include)
    c_code.append('#include"' + module_path_h + '"\n')
    # TODO: gather the includes needed to express before source code.
    c_code.append('\n')

    # Populate the symbol table before emitting function definitions so that
    # function references can be correctly constructed.
    self.populate_symbol_table_from_declarations(self.tree)

    # Emit the function definitions and declarations.
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

    return [SourceCodeFile(module_path_c, ''.join(c_code)), SourceCodeFile(module_path_h, ''.join(h_code))]


class ConverterToPython(HeadspaceConverter):

  def __init__(self, parse_tree):
    super().__init__(parse_tree)

  def emit_function_call(self, function_call_node, py_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or
           function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        py_code.append(' ' * indent_level)
        if function_call_node.members[0].members[2].members[0] == 'print' or function_call_node.members[0].members[2].members[0] == 'printInt':
          py_code.append('print(')
        if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
          py_code.append(function_call_node.members[1].members[1].members[0].members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
          for chain_entry in function_call_node.members[1].members[1].members[0].members:
            py_code.append(chain_entry.members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'FUNCTION_CALL'):
          self.emit_function_call(function_call_node.members[1].members[1].members[0], py_code, 0)
        py_code.append(', end="")\n')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        py_code.append(' ' * indent_level)
        # Emit the chain of identifiers.
        for chain_node in function_call_node.members[0].members:
          py_code.append(chain_node.members[0])
        # Emit the arguments for the function call.
        if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
          py_code.append('(')
          first_arg = True
          for argument_node in function_call_node.members[1].members[1].members:
            if not first_arg:
              py_code.append(' ,')
            if argument_node.node_type == 'NUMBER_LITERAL':
              py_code.append(argument_node.members[0])
              first_arg = False
          py_code.append(')')
        else:
          print('Function call was missing a list of arguments.')
          sys.exit(1)

  def emit_identifier_chain(self, identifier_chain_node, py_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        py_code.append(member.members[0])

  def emit_return_statement(self, return_statement_node, py_code, indent_level):
    if return_statement_node.members[0]:
      py_code.append(' ' * indent_level)
      py_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], py_code, indent_level)
      py_code.append('\n')

  def convert_operator(self, provided_operator):
    if provided_operator == '++':
      return ' += 1'
    elif provided_operator == '--':
      return ' -= 1'
    return provided_operator

  def convert_data_type(self, provided_type):
    if provided_type == 'int32':
      return 'int'
    elif provided_type == 'void':
      return 'None'
    else:
      return provided_type

  def emit_variable_declaration(self, variable_declaration, py_code, indent_level):
    # In python, variables do not need to be forward declared.
    pass

  def emit_assignment_statement(self, assignment_statement, py_code, indent_level):
    py_code.append(' ' * indent_level)
    # TODO: Need to introduce lvalue to be able to assign to things like function call return value.
    if assignment_statement.members[0].node_type == 'ASSIGNMENT_TARGET':
      py_code.append(assignment_statement.members[0].members[0])
    py_code.append(' = ')
    self.emit_code_statement(assignment_statement.members[2], py_code, 0)
    py_code.append('\n')

  def emit_if_statement(self, if_statement, py_code, indent_level):
    py_code.append(' ' * indent_level)
    py_code.append('if ')
    if if_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(if_statement.members[1], py_code, indent_level)
    py_code.append(':\n')
    self.emit_code_block(if_statement.members[2], py_code, indent_level)
    if len(if_statement.members) > 4 and if_statement.members[3].node_type == 'ELSE_KEYWORD':
      py_code.append(' ' * indent_level)
      py_code.append('else:\n')
      self.emit_code_block(if_statement.members[4], py_code, indent_level)

  def emit_while_statement(self, while_statement, py_code, indent_level):
    py_code.append(' ' * indent_level)
    py_code.append('while ')
    if while_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(while_statement.members[1], py_code, indent_level)
    py_code.append(':\n')
    self.emit_code_block(while_statement.members[2], py_code, indent_level)

  def emit_code_block(self, code_block_node, py_code, indent_level):
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, py_code, indent_level + 2)
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, py_code, 'PYTHON')
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, py_code, indent_level + 2)
      elif member.node_type == 'DECLARATION':
        self.emit_variable_declaration(member, py_code, indent_level + 2)
      elif member.node_type == 'ASSIGNMENT':
        self.emit_assignment_statement(member, py_code, indent_level + 2)
      elif member.node_type == 'IF_STATEMENT':
        self.emit_if_statement(member, py_code, indent_level + 2)
      elif member.node_type == 'WHILE_STATEMENT':
        self.emit_while_statement(member, py_code, indent_level + 2)
      elif member.node_type == 'POSTFIX_OPERATION':
        py_code.append(' ' * (indent_level + 2))
        self.emit_code_statement(member, py_code, 0)
        py_code.append('\n')

  def emit_function_body(self, function_body_node, py_code, indent_level):
    self.emit_code_block(function_body_node, py_code, indent_level)

  def emit_function_definition(self, function_declaration_node, py_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the module.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    py_code.append(' ' * indent_level)
    py_code.append('def ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      py_code.append(function_params[param_index][0] + ': ' + self.convert_data_type(function_params[param_index][1]) + ', ')
      param_index += 1
    if len(function_params) > 0:
      py_code.append(function_params[param_index][0] + ': ' + self.convert_data_type(function_params[param_index][1]))
    py_code.append(')')
    # Include the return type of the function.
    py_code.append(' -> ' + self.convert_data_type(return_type) + ':\n')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), py_code, indent_level)
    py_code.append('\n')

  def emit_code(self):
    py_code = []
    module_details = self.find_module_details()
    module_path_py = module_details.to_file_path('python') + '.py'

    self.populate_symbol_table_from_declarations(self.tree)

    for module in self.find_imports():
      import_module_details = self.symbol_table.find_symbol(module)
      py_code.append('import ' + convert_module_to_language_import(import_module_details, 'python') + ' as ' + module + '\n')

    for module_level_member in self.tree.members:
      if module_level_member.node_type == 'FUNCTION_DECLARATION':
        self.emit_function_definition(module_level_member, py_code, 0)

    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      py_code.append('def main():\n')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, py_code, 0)
      py_code.append('\nif __name__ == \'__main__\':\n  main()\n')

    python_files = [SourceCodeFile(module_path_py, ''.join(py_code))]

    # We need to create __init__.py files for each of the packages in the module's path.
    package_index = 0
    package_layers = []
    while package_index < len(module_details.package_name_parts):
      package_layers.append(module_details.package_name_parts[package_index])
      package_index += 1
      init_file_path = os.path.join(*package_layers, '__init__.py')
      # Create an empty init file for this package.
      python_files.append(SourceCodeFile(init_file_path, ''))

    return python_files


class ConverterToGo(HeadspaceConverter):

  def __init__(self, parse_tree):
    super().__init__(parse_tree)
    self.required_imports = []

  def emit_function_call(self, function_call_node, go_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or
           function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        go_code.append('\t' * indent_level)
        if function_call_node.members[0].members[2].members[0] == 'print':
          go_code.append('fmt.Print(')
          if '"fmt"' not in self.required_imports:
            self.required_imports.append('"fmt"')
        elif function_call_node.members[0].members[2].members[0] == 'printInt':
          go_code.append('fmt.Printf("%d", ')
          if '"fmt"' not in self.required_imports:
            self.required_imports.append('"fmt"')
        if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
          go_code.append(function_call_node.members[1].members[1].members[0].members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
          for chain_entry in function_call_node.members[1].members[1].members[0].members:
            go_code.append(chain_entry.members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'FUNCTION_CALL'):
          self.emit_function_call(function_call_node.members[1].members[1].members[0], go_code, 0)
        go_code.append(')')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        go_code.append('\t' * indent_level)
        # Emit the chain of identifiers.
        i = 0
        num_identifiers = len(function_call_node.members[0].members)
        while i < num_identifiers - 1:
          go_code.append(function_call_node.members[0].members[i].members[0])
          i += 1
        # Capitalize the first letter of the function call.
        go_code.append(capitalize_first_letter(function_call_node.members[0].members[num_identifiers-1].members[0]))
        # Emit the arguments for the function call.
        if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
          go_code.append('(')
          first_arg = True
          for argument_node in function_call_node.members[1].members[1].members:
            if not first_arg:
              go_code.append(' ,')
            if argument_node.node_type == 'NUMBER_LITERAL':
              go_code.append(argument_node.members[0])
              first_arg = False
          go_code.append(')')
        else:
          print('Function call was missing a list of arguments.')
          sys.exit(1)

  def emit_identifier_chain(self, identifier_chain_node, go_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        go_code.append(member.members[0])

  def emit_return_statement(self, return_statement_node, go_code, indent_level):
    if return_statement_node.members[0]:
      go_code.append('\t' * indent_level)
      go_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], go_code, indent_level)
      go_code.append('\n')

  def convert_data_type(self, provided_type):
    # Note the int32 type is the same in Go.
    return provided_type

  def emit_variable_declaration(self, variable_declaration, go_code, indent_level):
    go_code.append('\t' * indent_level)
    go_code.append('var ' + variable_declaration.members[0].members[0] + ' ' + self.convert_data_type(variable_declaration.members[2].members[0]) + '\n')

  def emit_assignment_statement(self, assignment_statement, go_code, indent_level):
    go_code.append('\t' * indent_level)
    # TODO: Need to introduce lvalue to be able to assign to things like function call return value.
    if assignment_statement.members[0].node_type == 'ASSIGNMENT_TARGET':
      go_code.append(assignment_statement.members[0].members[0])
    go_code.append(' = ')
    self.emit_code_statement(assignment_statement.members[2], go_code, 0)
    go_code.append('\n')

  def emit_if_statement(self, if_statement, go_code, indent_level):
    go_code.append('\t' * indent_level)
    go_code.append('if ')
    if if_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(if_statement.members[1], go_code, indent_level)
    go_code.append(' ')
    self.emit_code_block(if_statement.members[2], go_code, indent_level)
    if len(if_statement.members) > 4 and if_statement.members[3].node_type == 'ELSE_KEYWORD':
      go_code.append(' else ')
      self.emit_code_block(if_statement.members[4], go_code, indent_level)
    go_code.append('\n')

  def emit_while_statement(self, while_statement, go_code, indent_level):
    go_code.append('\t' * indent_level)
    go_code.append('for ')
    if while_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(while_statement.members[1], go_code, indent_level)
    go_code.append(' ')
    self.emit_code_block(while_statement.members[2], go_code, indent_level)
    go_code.append('\n')

  def emit_code_block(self, code_block_node, go_code, indent_level):
    go_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, go_code, indent_level + 1)
        go_code.append('\n')
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, go_code, 'GO')
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, go_code, indent_level + 1)
      elif member.node_type == 'DECLARATION':
        self.emit_variable_declaration(member, go_code, indent_level + 1)
      elif member.node_type == 'ASSIGNMENT':
        self.emit_assignment_statement(member, go_code, indent_level + 1)
      elif member.node_type == 'IF_STATEMENT':
        self.emit_if_statement(member, go_code, indent_level + 1)
      elif member.node_type == 'WHILE_STATEMENT':
        self.emit_while_statement(member, go_code, indent_level + 1)
      elif member.node_type == 'POSTFIX_OPERATION':
        go_code.append('\t' * (indent_level + 1))
        self.emit_code_statement(member, go_code, 0)
        go_code.append('\n')
    if indent_level > 0:
      go_code.append('\t' * indent_level)
    go_code.append('}')

  def emit_function_body(self, function_body_node, go_code, indent_level):
    self.emit_code_block(function_body_node, go_code, indent_level)

  def emit_function_definition(self, function_declaration_node, go_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the Go module.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = capitalize_first_letter(find_function_identifier(function_declaration_node))
    function_params = find_function_parameters(function_declaration_node)
    go_code.append('\t' * indent_level)
    go_code.append('func ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      go_code.append(function_params[param_index][0] + ' ' + self.convert_data_type(function_params[param_index][1]) + ', ')
      param_index += 1
    if len(function_params) > 0:
      go_code.append(function_params[param_index][0] + ' ' + self.convert_data_type(function_params[param_index][1]))
    go_code.append(')')
    # Include the return type of the function.
    if return_type == 'void':
      go_code.append(' ')
    else:
      go_code.append(' ' + self.convert_data_type(return_type) + ' ')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), go_code, indent_level)
    go_code.append('\n')

  def emit_code(self):
    go_code = []
    module_details = self.find_module_details()
    main_function_declaration = find_main_function(self.tree)

    # Note: use go mod init to install a library
    go_body_code = []
    for module_level_member in self.tree.members:
      if module_level_member.node_type == 'FUNCTION_DECLARATION':
        self.emit_function_definition(module_level_member, go_body_code, 0)

    if main_function_declaration:
      go_body_code.append('func main() ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, go_body_code, 0)
              go_body_code.append('\n')

    self.populate_symbol_table_from_declarations(self.tree)

    if main_function_declaration:
      go_code.append('package main\n\n')
    else:
      go_code.append('package ' + module_details.to_namespace('go') + '\n\n')

    for import_lib in self.required_imports:
      go_code.append('import ' + import_lib + '\n')

    for module in self.find_imports():
      import_module_details = self.symbol_table.find_symbol(module)
      go_code.append('import ' + module + ' "' + convert_module_to_language_import(import_module_details, 'go') + '"\n')
    go_code.append('\n')

    go_code.extend(go_body_code)

    if main_function_declaration:
      # Create file name with a main.go module.
      main_module_filename = os.path.join(module_details.module_name, 'main.go')
      return [SourceCodeFile(main_module_filename, ''.join(go_code))]
    else:
      # This module has no main function, so it is only a library.
      return [SourceCodeFile(module_details.module_name + '.go', ''.join(go_code))]


class ConverterToJavaScript(HeadspaceConverter):

  def __init__(self, parse_tree):
    super().__init__(parse_tree)

  def emit_function_call(self, function_call_node, js_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or
           function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        js_code.append(' ' * indent_level)
        if function_call_node.members[0].members[2].members[0] == 'print':
          js_code.append('process.stdout.write(')
        elif function_call_node.members[0].members[2].members[0] == 'printInt':
          js_code.append('process.stdout.write("" + ')
        if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
          js_code.append(function_call_node.members[1].members[1].members[0].members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
          for chain_entry in function_call_node.members[1].members[1].members[0].members:
            js_code.append(chain_entry.members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'FUNCTION_CALL'):
          self.emit_function_call(function_call_node.members[1].members[1].members[0], js_code, 0)
        js_code.append(')')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        js_code.append(' ' * indent_level)
        # Emit the chain of identifiers.
        for chain_node in function_call_node.members[0].members:
          js_code.append(chain_node.members[0])
        # Emit the arguments for the function call.
        if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
          js_code.append('(')
          first_arg = True
          for argument_node in function_call_node.members[1].members[1].members:
            if not first_arg:
              js_code.append(' ,')
            if argument_node.node_type == 'NUMBER_LITERAL':
              js_code.append(argument_node.members[0])
              first_arg = False
          js_code.append(')')
        else:
          print('Function call was missing a list of arguments.')
          sys.exit(1)

  def emit_identifier_chain(self, identifier_chain_node, js_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        js_code.append(member.members[0])

  def emit_return_statement(self, return_statement_node, js_code, indent_level):
    if return_statement_node.members[0]:
      js_code.append(' ' * indent_level)
      js_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], js_code, indent_level)
      js_code.append(';\n')

  def convert_data_type(self, provided_type):
    if provided_type == 'int32':
      return 'number'
    return provided_type

  def emit_variable_declaration(self, variable_declaration, js_code, indent_level):
    js_code.append(' ' * indent_level)
    # Note that JS variables aren't declared with a data type.
    js_code.append('let ' + variable_declaration.members[0].members[0] + ';\n')

  def emit_assignment_statement(self, assignment_statement, js_code, indent_level):
    js_code.append(' ' * indent_level)
    # TODO: Need to introduce lvalue to be able to assign to things like function call return value.
    if assignment_statement.members[0].node_type == 'ASSIGNMENT_TARGET':
      js_code.append(assignment_statement.members[0].members[0])
    js_code.append(' = ')
    self.emit_code_statement(assignment_statement.members[2], js_code, 0)
    js_code.append(';\n')

  def emit_if_statement(self, if_statement, js_code, indent_level):
    js_code.append(' ' * indent_level)
    js_code.append('if (')
    if if_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(if_statement.members[1], js_code, indent_level)
    js_code.append(') ')
    self.emit_code_block(if_statement.members[2], js_code, indent_level)
    if len(if_statement.members) > 4 and if_statement.members[3].node_type == 'ELSE_KEYWORD':
      js_code.append(' else ')
      self.emit_code_block(if_statement.members[4], js_code, indent_level)
    js_code.append('\n')

  def emit_while_statement(self, while_statement, js_code, indent_level):
    js_code.append(' ' * indent_level)
    js_code.append('while (')
    if while_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(while_statement.members[1], js_code, indent_level)
    js_code.append(') ')
    self.emit_code_block(while_statement.members[2], js_code, indent_level)
    js_code.append('\n')

  def emit_code_block(self, code_block_node, js_code, indent_level):
    js_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, js_code, indent_level + 2)
        js_code.append(';\n')
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, js_code, 'JS')
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, js_code, indent_level + 2)
      elif member.node_type == 'DECLARATION':
        self.emit_variable_declaration(member, js_code, indent_level + 2)
      elif member.node_type == 'ASSIGNMENT':
        self.emit_assignment_statement(member, js_code, indent_level + 2)
      elif member.node_type == 'IF_STATEMENT':
        self.emit_if_statement(member, js_code, indent_level + 2)
      elif member.node_type == 'WHILE_STATEMENT':
        self.emit_while_statement(member, js_code, indent_level + 2)
      elif member.node_type == 'POSTFIX_OPERATION':
        js_code.append(' ' * (indent_level + 2))
        self.emit_code_statement(member, js_code, 0)
        js_code.append(';\n')
    if indent_level > 0:
      js_code.append(' ' * indent_level)
    #js_code.append('}\n')
    js_code.append('}')

  def emit_function_body(self, function_body_node, js_code, indent_level):
    self.emit_code_block(function_body_node, js_code, indent_level)

  def emit_function_definition(self, function_declaration_node, js_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the JavaScript.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    js_code.append(' ' * indent_level)
    param_index = 0
    js_code.append(' ' * indent_level)
    js_code.append('/**\n')
    while param_index < len(function_params):
      js_code.append(' ' * indent_level)
      js_code.append(' * @param {' + self.convert_data_type(function_params[param_index][1]) + '} ' + function_params[param_index][0] + '\n')
      param_index += 1
    js_code.append(' ' * indent_level)
    js_code.append(' * @returns {' + self.convert_data_type(return_type) + '}\n')
    js_code.append(' ' * indent_level)
    js_code.append(' */\n')
    js_code.append(' ' * indent_level)
    js_code.append('export function ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      js_code.append(function_params[param_index][0] + ', ')
      param_index += 1
    if len(function_params) > 0:
      js_code.append(function_params[param_index][0])
    js_code.append(') ')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), js_code, indent_level)
    js_code.append('\n')

  def emit_code(self):
    js_code = []
    module_details = self.find_module_details()

    self.populate_symbol_table_from_declarations(self.tree)

    for module in self.find_imports():
      import_module_details = self.symbol_table.find_symbol(module)
      import_module_name = convert_module_to_language_import(import_module_details, 'javascript')
      import_module_file = import_module_name + '.js'
      js_code.append('import * as ' + module + ' from "./' + import_module_file + '";\n')
    js_code.append('\n')

    for module_level_member in self.tree.members:
      if module_level_member.node_type == 'FUNCTION_DECLARATION':
        self.emit_function_definition(module_level_member, js_code, 0)

    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      js_code.append('function main() ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, js_code, 0)
      js_code.append('\nmain();\n')

    #module_filename = module_name + '.js'
    module_filename = module_details.module_name + '.js'

    # Include a package.json to support exporting public functions in a module.
    package_json_content = '{\n  "type": "module"\n}\n'

    return [SourceCodeFile(module_filename, ''.join(js_code)), SourceCodeFile('package.json', package_json_content)]



class ConverterToJava(HeadspaceConverter):

  def __init__(self, parse_tree):
    super().__init__(parse_tree)

  def emit_function_call(self, function_call_node, java_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or
           function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        if (function_call_node.members[0].members[2].members[0] == 'print' or
            function_call_node.members[0].members[2].members[0] == 'printInt'):
          java_code.append('System.out.print(')
        if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
          java_code.append(function_call_node.members[1].members[1].members[0].members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
          for chain_entry in function_call_node.members[1].members[1].members[0].members:
            java_code.append(chain_entry.members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'FUNCTION_CALL'):
          self.emit_function_call(function_call_node.members[1].members[1].members[0], java_code, 0)
        java_code.append(')')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        # Emit the chain of identifiers.
        for chain_node in function_call_node.members[0].members:
          symbol_for_name = self.symbol_table.find_symbol(chain_node.members[0])
          if type(symbol_for_name) == ModuleDetails:
            # The first member in the chain is a module, use the class name to reference the static function.
            java_code.append(chain_node.members[0].capitalize())
          else:
            java_code.append(chain_node.members[0])
        # Emit the arguments for the function call.
        if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
          java_code.append('(')
          first_arg = True
          for argument_node in function_call_node.members[1].members[1].members:
            if not first_arg:
              java_code.append(' ,')
            if argument_node.node_type == 'NUMBER_LITERAL':
              java_code.append(argument_node.members[0])
              first_arg = False
          java_code.append(')')
        else:
          print('Function call was missing a list of arguments.')
          sys.exit(1)

  def emit_identifier_chain(self, identifier_chain_node, java_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        java_code.append(member.members[0])

  def emit_return_statement(self, return_statement_node, java_code, indent_level):
    if return_statement_node.members[0]:
      java_code.append(' ' * indent_level)
      java_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], java_code, indent_level)
      java_code.append(';\n')

  def convert_data_type(self, provided_type):
    if provided_type == 'int32':
      return 'int'
    else:
      return provided_type

  def emit_variable_declaration(self, variable_declaration, java_code, indent_level):
    java_code.append(' ' * indent_level)
    java_code.append(self.convert_data_type(variable_declaration.members[2].members[0]) + ' ' + variable_declaration.members[0].members[0] + ';\n')

  def emit_assignment_statement(self, assignment_statement, java_code, indent_level):
    java_code.append(' ' * indent_level)
    # TODO: Need to introduce lvalue to be able to assign to things like function call return value.
    if assignment_statement.members[0].node_type == 'ASSIGNMENT_TARGET':
      java_code.append(assignment_statement.members[0].members[0])
    java_code.append(' = ')
    self.emit_code_statement(assignment_statement.members[2], java_code, 0)
    java_code.append(';\n')

  def emit_if_statement(self, if_statement, java_code, indent_level):
    java_code.append(' ' * indent_level)
    java_code.append('if (')
    if if_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(if_statement.members[1], java_code, indent_level)
    java_code.append(') ')
    self.emit_code_block(if_statement.members[2], java_code, indent_level)
    if len(if_statement.members) > 4 and if_statement.members[3].node_type == 'ELSE_KEYWORD':
      java_code.append(' else ')
      self.emit_code_block(if_statement.members[4], java_code, indent_level)
    java_code.append('\n')

  def emit_while_statement(self, while_statement, java_code, indent_level):
    java_code.append(' ' * indent_level)
    java_code.append('while (')
    if while_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(while_statement.members[1], java_code, indent_level)
    java_code.append(') ')
    self.emit_code_block(while_statement.members[2], java_code, indent_level)
    java_code.append('\n')

  def emit_code_block(self, code_block_node, java_code, indent_level):
    java_code.append('{\n')
    java_code.append(' ' * (indent_level + 2))
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, java_code, indent_level + 2)
        java_code.append(';\n');
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, java_code, 'JAVA')
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, java_code, indent_level + 2)
      elif member.node_type == 'DECLARATION':
        self.emit_variable_declaration(member, java_code, indent_level + 2)
      elif member.node_type == 'ASSIGNMENT':
        self.emit_assignment_statement(member, java_code, indent_level + 2)
      elif member.node_type == 'IF_STATEMENT':
        self.emit_if_statement(member, java_code, indent_level + 2)
      elif member.node_type == 'WHILE_STATEMENT':
        self.emit_while_statement(member, java_code, indent_level + 2)
      elif member.node_type == 'POSTFIX_OPERATION':
        self.emit_code_statement(member, java_code, 0)
        java_code.append(';\n')
    if indent_level > 0:
      java_code.append(' ' * indent_level)
    java_code.append('}')

  def emit_function_body(self, function_body_node, java_code, indent_level):
    self.emit_code_block(function_body_node, java_code, indent_level)

  def emit_function_definition(self, function_declaration_node, java_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the Java class.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    java_code.append(' ' * indent_level)
    java_code.append('public static ' + self.convert_data_type(return_type) + ' ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      java_code.append(self.convert_data_type(function_params[param_index][1]) + ' ' + function_params[param_index][0] + ', ')
      param_index += 1
    if len(function_params) > 0:
      java_code.append(self.convert_data_type(function_params[len(function_params) - 1][1]) + ' ' + function_params[len(function_params) - 1][0])
    java_code.append(') ')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), java_code, indent_level)

  def emit_code(self):
    java_code = []
    module_details = self.find_module_details()

    self.populate_symbol_table_from_declarations(self.tree)

    # Declare the package for this Java module.
    # Should be for example: com.jeffscudder.tests.projects;
    java_code.append('package ' + module_details.to_namespace('java') + ';\n\n')

    for module in self.find_imports():
      import_module_details = self.symbol_table.find_symbol(module)
      import_module_classpath = convert_module_to_language_import(import_module_details, 'java')
      java_code.append('import ' + import_module_classpath + ';\n')
    java_code.append('\n')

    java_class_name = capitalize_first_letter(module_details.module_name)
    java_code.append('public class ' + java_class_name + '\n')
    java_code.append('{\n')

    for module_level_member in self.tree.members:
      if module_level_member.node_type == 'FUNCTION_DECLARATION':
        self.emit_function_definition(module_level_member, java_code, 2)

    main_function_declaration = find_main_function(self.tree)
    if main_function_declaration:
      java_code.append('  public static void main(String[] args) ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, java_code, 2)
    java_code.append('\n}\n')
    # Create file name with a .java class file.
    java_class_filename = os.path.join(module_details.to_file_path('java'), java_class_name + '.java')
    return [SourceCodeFile(java_class_filename, ''.join(java_code))]


class ConverterToDotNet(HeadspaceConverter):

  def __init__(self, parse_tree):
    super().__init__(parse_tree)

  def emit_function_call(self, function_call_node, dotnet_code, indent_level):
    if function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
      # Handle a print function.
      dotnet_code.append(' ' * indent_level)
      if (function_call_node.members[0].members[0].node_type == 'IDENTIFIER' and
          function_call_node.members[0].members[0].members[0] == 'os' and
          function_call_node.members[0].members[2].node_type == 'IDENTIFIER' and
          (function_call_node.members[0].members[2].members[0] == 'print' or
           function_call_node.members[0].members[2].members[0] == 'printInt') and
          function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS'):
        if (function_call_node.members[0].members[2].members[0] == 'print' or
            function_call_node.members[0].members[2].members[0] == 'printInt'):
          dotnet_code.append('Console.Write(')
        if (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
            function_call_node.members[1].members[1].members[0].node_type == 'STRING_LITERAL'):
          dotnet_code.append(function_call_node.members[1].members[1].members[0].members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'IDENTIFIER_CHAIN'):
          for chain_entry in function_call_node.members[1].members[1].members[0].members:
            dotnet_code.append(chain_entry.members[0])
        elif (function_call_node.members[1].members[1].node_type == 'ARGUMENTS' and
              function_call_node.members[1].members[1].members[0].node_type == 'FUNCTION_CALL'):
          self.emit_function_call(function_call_node.members[1].members[1].members[0], dotnet_code, 0)
        dotnet_code.append(')')
      elif function_call_node.members[0].node_type == 'IDENTIFIER_CHAIN':
        # Emit the chain of identifiers.
        for chain_node in function_call_node.members[0].members:
          symbol_for_name = self.symbol_table.find_symbol(chain_node.members[0])
          if type(symbol_for_name) == ModuleDetails:
            # The first member in the chain is a module, use the class name to reference the static function.
            dotnet_code.append(chain_node.members[0].capitalize())
          else:
            dotnet_code.append(chain_node.members[0])
        # Emit the arguments for the function call.
        if function_call_node.members[1].node_type == 'FUNCTION_CALL_ARGUMENTS':
          dotnet_code.append('(')
          first_arg = True
          for argument_node in function_call_node.members[1].members[1].members:
            if not first_arg:
              dotnet_code.append(' ,')
            if argument_node.node_type == 'NUMBER_LITERAL':
              dotnet_code.append(argument_node.members[0])
              first_arg = False
          dotnet_code.append(')')
        else:
          print('Function call was missing a list of arguments.')
          sys.exit(1)

  def emit_identifier_chain(self, identifier_chain_node, dotnet_code, indent_level):
    for member in identifier_chain_node.members:
      if member.node_type == 'IDENTIFIER':
        dotnet_code.append(member.members[0])

  def emit_return_statement(self, return_statement_node, dotnet_code, indent_level):
    if return_statement_node.members[0]:
      dotnet_code.append(' ' * indent_level)
      dotnet_code.append('return ')
      self.emit_code_statement(return_statement_node.members[0], dotnet_code, indent_level)
      dotnet_code.append(';\n')

  def convert_data_type(self, provided_type):
    if provided_type == 'int32':
      return 'int'
    else:
      return provided_type

  def emit_variable_declaration(self, variable_declaration, dotnet_code, indent_level):
    dotnet_code.append(' ' * indent_level)
    dotnet_code.append(self.convert_data_type(variable_declaration.members[2].members[0]) + ' ' + variable_declaration.members[0].members[0] + ';\n')

  def emit_assignment_statement(self, assignment_statement, dotnet_code, indent_level):
    dotnet_code.append(' ' * indent_level)
    # TODO: Need to introduce lvalue to be able to assign to things like function call return value.
    if assignment_statement.members[0].node_type == 'ASSIGNMENT_TARGET':
      dotnet_code.append(assignment_statement.members[0].members[0])
    dotnet_code.append(' = ')
    self.emit_code_statement(assignment_statement.members[2], dotnet_code, 0)
    dotnet_code.append(';\n')

  def emit_if_statement(self, if_statement, dotnet_code, indent_level):
    dotnet_code.append(' ' * indent_level)
    dotnet_code.append('if (')
    if if_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(if_statement.members[1], dotnet_code, indent_level)
    dotnet_code.append(') ')
    self.emit_code_block(if_statement.members[2], dotnet_code, indent_level)
    if len(if_statement.members) > 4 and if_statement.members[3].node_type == 'ELSE_KEYWORD':
      dotnet_code.append(' else ')
      self.emit_code_block(if_statement.members[4], dotnet_code, indent_level)
    dotnet_code.append('\n')

  def emit_while_statement(self, while_statement, dotnet_code, indent_level):
    dotnet_code.append(' ' * indent_level)
    dotnet_code.append('while (')
    if while_statement.members[1].node_type == 'CONDITION_EXPRESSION':
      self.emit_condition_expression(while_statement.members[1], dotnet_code, indent_level)
    dotnet_code.append(') ')
    self.emit_code_block(while_statement.members[2], dotnet_code, indent_level)
    dotnet_code.append('\n')

  def emit_code_block(self, code_block_node, dotnet_code, indent_level):
    dotnet_code.append('{\n')
    for member in code_block_node.members:
      if member.node_type == 'FUNCTION_CALL':
        self.emit_function_call(member, dotnet_code, indent_level + 2)
        dotnet_code.append(';\n')
      elif member.node_type == 'FOREIGN_CODE_BLOCK':
        self.emit_foreign_code_block(member, dotnet_code, 'DOTNET')
      elif member.node_type == 'RETURN_STATEMENT':
        self.emit_return_statement(member, dotnet_code, indent_level + 2)
      elif member.node_type == 'DECLARATION':
        self.emit_variable_declaration(member, dotnet_code, indent_level + 2)
      elif member.node_type == 'ASSIGNMENT':
        self.emit_assignment_statement(member, dotnet_code, indent_level + 2)
      elif member.node_type == 'IF_STATEMENT':
        self.emit_if_statement(member, dotnet_code, indent_level + 2)
      elif member.node_type == 'WHILE_STATEMENT':
        self.emit_while_statement(member, dotnet_code, indent_level + 2)
      elif member.node_type == 'POSTFIX_OPERATION':
        self.emit_code_statement(member, dotnet_code, indent_level + 2)
        dotnet_code.append(';\n')
    if indent_level > 0:
      dotnet_code.append(' ' * indent_level)
    dotnet_code.append('}')

  def emit_function_body(self, function_body_node, dotnet_code, indent_level):
    self.emit_code_block(function_body_node, dotnet_code, indent_level)

  def emit_function_definition(self, function_declaration_node, dotnet_code, indent_level):
    # Skip the main function because we have special case logic to place it at the end of the MainProgram class.
    if function_declaration_node.members[0].node_type == 'IDENTIFIER' and function_declaration_node.members[0].members[0] == 'main':
      return
    return_type = find_function_return_type(function_declaration_node)
    function_name = find_function_identifier(function_declaration_node)
    function_params = find_function_parameters(function_declaration_node)
    dotnet_code.append(' ' * indent_level)
    dotnet_code.append('public static ' + self.convert_data_type(return_type) + ' ' + function_name + '(')
    param_index = 0
    while param_index < len(function_params) - 1:
      dotnet_code.append(self.convert_data_type(function_params[param_index][1]) + ' ' + function_params[param_index][0] + ', ')
      param_index += 1
    if len(function_params) > 0:
      dotnet_code.append(self.convert_data_type(function_params[len(function_params) - 1][1]) + ' ' + function_params[len(function_params) - 1][0])
    dotnet_code.append(') ')
    # Now emit the code block body of the function.
    self.emit_function_body(find_function_body_code_block(function_declaration_node), dotnet_code, indent_level)
    dotnet_code.append('\n')

  def emit_code(self):
    dotnet_code = []
    module_details = self.find_module_details()
    main_function_declaration = find_main_function(self.tree)

    dotnet_class_name = capitalize_first_letter(module_details.module_name)
    dotnet_code.append('using System;\n')

    for module in self.find_imports():
      import_module_details = self.symbol_table.find_symbol(module)
      import_module_classpath = convert_module_to_language_import(import_module_details, 'dotnet')
      dotnet_code.append('using ' + import_module_classpath + ';\n')
    dotnet_code.append('\n')

    dotnet_code.append('\n')
    dotnet_code.append('namespace ' + module_details.to_namespace('dotnet') + ' {\n')

    self.populate_symbol_table_from_declarations(self.tree)

    dotnet_class_name = capitalize_first_letter(module_details.module_name)

    dotnet_code.append('  class ' + dotnet_class_name + ' {\n')
    for module_level_member in self.tree.members:
      if module_level_member.node_type == 'FUNCTION_DECLARATION':
        self.emit_function_definition(module_level_member, dotnet_code, 4)

    output_files = []

    if main_function_declaration:
      dotnet_code.append('    static void Main(string[] args) ')
      for member in main_function_declaration.members:
        if member.node_type == 'FUNCTION_DEFINITION':
          for def_member in member.members:
            if def_member.node_type == 'CODE_BLOCK':
              self.emit_code_block(def_member, dotnet_code, 4)
    dotnet_code.append('\n  }\n')
    dotnet_code.append('}\n')

    if main_function_declaration:
      # Create file name with a .cs (C#) module.
      dotnet_class_filename = os.path.join(module_details.to_file_path('dotnet'), dotnet_class_name + '.cs')
      output_files.append(SourceCodeFile(dotnet_class_filename, ''.join(dotnet_code)))
      # Since there is a main function, this package must also contain a .csproj config file.
      csproj_filename = os.path.join(module_details.to_file_path('dotnet'), 'headspace.csproj')
      output_files.append(SourceCodeFile(csproj_filename, ''.join(DOTNET_CSPROJ_CONFIG)))
    else:
      # There is no main function, so create a library module.
      dotnet_class_filename = os.path.join(module_details.to_file_path('dotnet'), dotnet_class_name + '.cs')
      output_files.append(SourceCodeFile(dotnet_class_filename, ''.join(dotnet_code)))
    return output_files


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


def convert_filename(filename, target_language):
  with open(filename, 'r') as source_file:
    source_code = source_file.read()
  source_tree = parser.parse_source(source_code)
  results_files = convert(source_tree, target_language)
  for result_file in results_files:
    with open(result_file.filename, 'w') as output_file:
      output_file.write(result_file.content)


if __name__ == '__main__':
  if len(sys.argv) < 3:
    print('To compile the Headspace source code, you must specify the headspace file and target language')
    sys.exit(1)
  convert_filename(sys.argv[1], sys.argv[2])

