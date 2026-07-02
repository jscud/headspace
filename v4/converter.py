import parser
import sys
import os

# Checklist for converting headspace parse trees to target languages:
#   FEATURE NAME                         SUPPORTED LANGUAGES
# - creating main function               c  py  go  js  java  c#
# - print statement                      c  py  go  js  java  c#


class SourceFile:

  def __init__(self):
    self.file_path = ''
    self.parts = []

  def content(self):
    return ''.join(self.parts)

  def print(self):
    print('-------------------')
    print('File name:', self.file_path)
    print('Content:')
    print(self.content())
    print('-------------------')

  def add_code(self, code):
    self.parts.append(code)

class SymbolTable:

  def __init__(self, parent_table=None):
    self.parent_table = parent_table
    self.symbols = {}

  def find_symbol(self, name):
    if name in self.symbols:
      return self.symbols[name]
    elif self.parent_table:
      return self.parent_table.find_symbol(name)

  def set_symbol(self, name, symbol_type):
    self.symbols[name] = symbol_type


def capitalize_first_letter(input_str):
  return input_str[0].capitalize() + input_str[1:]


class ModuleInfo:

  def __init__(self, module_id):
    self.module_id = module_id
    self.symbol_table = SymbolTable()
    segments = module_id.strip('"').split('/')
    if len(segments) < 3:
      sys.exit('A moduleName must be in the form "domainName.tld/package/module".')
    self.domain_full = segments[0]
    self.domain_prefix = self.domain_full.split('.')[0]
    self.package_name_parts = segments[1:-1]
    self.module_name = segments[-1]

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
      capitalized_package_name_parts = [capitalize_first_letter(name) for name in self.package_name_parts]
      return '.'.join(capitalized_package_name_parts)
    return ''

  # Note that when a module is imported, it should be parsed and its symbol table populated.
  def to_file_path(self, target_language):
    # Note for C that we avoid adding the .c or .h suffix.
    if target_language == 'c' or target_language == 'py':
      return os.path.join(*self.package_name_parts, self.module_name)
    elif target_language == 'java':
      java_path_parts = self.domain_full.split('.')
      java_path_parts.reverse()
      java_path_parts.extend(self.package_name_parts)
      return os.path.join(*java_path_parts)
    elif target_language == 'dotnet':
      return self.to_namespace(target_language)
    return ''


class ClassDef:

  def __init__(self):
    self.class_name = ''
    self.symbol_table = SymbolTable()
    self.parent_module = None


class MemberDef:

  def __init__(self):
    self.member_name = ''
    self.member_type = ''
    self.parent_class = None


class MethodDef:

  def __init__(self):
    self.method_name = ''
    self.return_type = ''
    self.parent_class = None
    self.symbol_table = SymbolTable()


# Note the variable def is also used for parameters.
class VariableDef:

  def __init__(self):
    self.variable_name = ''
    self.variable_type = ''
    self.parent_container = None


class FunctionDef:

  def __init__(self):
    self.function_name = ''
    self.return_type = ''
    self.parent_module = None
    self.symbol_table = SymbolTable()


DOTNET_CSPROJ_CONFIG = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
"""


class Converter:

  def __init__(self, parse_tree, target_language, debug_print=False):
    self.tree = parse_tree
    self.module_symbol_table = SymbolTable()
    self.target_language = target_language
    self.debug_print = debug_print
    self.debug_indent = 0
    self.required_imports = []
    # Language specific source files to append to as the parse tree is
    # converted.
    self.c_src = None
    self.h_src = None
    self.py_src = None
    self.go_main_src = None
    self.js_src = None
    self.js_package = None
    self.java_main_src = None
    self.java_class_srcs = None
    self.dotnet_main_src = None
    self.csproj_src = None
    self.dotnet_class_srcs = None

  def emit_code(self):
    # Start by populating symbols in the module.
    self.populate_symbols()
    self.populate_source_files()
    self.emit_imports()
    for top_node in self.tree.members:
      pass
    # We place main at the end or in a seperate module if required by the
    # language.
    if self.has_main_function():
      self.emit_main()
    if self.target_language == 'c':
      return [self.c_src, self.h_src]
    elif self.target_language == 'py':
      return [self.py_src]
    elif self.target_language == 'go':
      if self.has_main_function():
        return [self.go_main_src]
    elif self.target_language == 'js':
      return [self.js_src, self.js_package]
    elif self.target_language == 'java':
      srcs = [self.java_main_src]
      srcs.extend(self.java_class_srcs)
      return srcs
    elif self.target_language == 'dotnet':
      srcs = [self.dotnet_main_src, self.csproj_src]
      srcs.extend(self.dotnet_class_srcs)
      return srcs
    else:
      return []

  def extract_type(self, type_chain_node):
    type_parts = []
    if type_chain_node.node_type != 'TYPE_CHAIN':
      sys.exit('Expected to extract the type from a type chain node.')
    for type_member in type_chain_node.members:
      if type_member.node_type == 'INITIAL_TYPE':
        type_parts.append(type_member.members[0])
      else:
        # TODO: handle follow on members in the chain.
        print('member node:')
        type_member.print()
    return ''.join(type_parts)

  def populate_symbols(self):
    """Analyzes the parse tree to find all definitions to populate nested symbol tables."""
    self.debug_node('overall module tree', self.tree)
    for node in self.tree.members:
      if node.node_type == 'MODULE_ID':
        module_info = ModuleInfo(node.members[0].strip('"'))
        self.module_symbol_table.symbols['module'] = module_info
      elif node.node_type == 'FUNCTION_DECLARATION':
        function_def = FunctionDef()
        for func_def_node in node.members:
          if func_def_node.node_type == 'FUNCTION_NAME':
            function_def.function_name = func_def_node.members[0]
          elif func_def_node.node_type == 'TYPE_CHAIN':
            function_def.return_type = self.extract_type(func_def_node)
          # TODO: process the parameters for the function and add them to the
          # function's symbol table since they will be in scope within the
          # function body's code block.
        self.module_symbol_table.symbols[function_def.function_name] = function_def
      else:
        # TODO: handle remaining node types.
        print('checking node:')
        node.print()

  def has_main_function(self):
    main_function = self.module_symbol_table.find_symbol('main')
    return main_function and type(main_function) == FunctionDef

  def find_main_function_node(self):
    for top_node in self.tree.members:
      if top_node.node_type == 'FUNCTION_DECLARATION' and top_node.members[0].node_type == 'FUNCTION_NAME' and top_node.members[0].members[0] == 'main':
        return top_node
    return None

  def populate_source_files(self):
    # Based on target language, create source file containers.
    if not 'module' in self.module_symbol_table.symbols or not self.module_symbol_table.symbols['module']:
      sys.exit('Unable to populate source files without a module ID.')
    module = self.module_symbol_table.symbols['module']
    if self.target_language == 'c':
      self.c_src = SourceFile()
      self.c_src.file_path = module.to_file_path(self.target_language) + '.c'
      self.h_src = SourceFile()
      self.h_src.file_path = module.to_file_path(self.target_language) + '.h'
    elif self.target_language == 'py':
      self.py_src = SourceFile()
      self.py_src.file_path = module.to_file_path(self.target_language) + '.py'
    elif self.target_language == 'go':
      self.go_main_src = SourceFile()
      # TODO: only populate main.go if there's a main function in the module.
      self.go_main_src.file_path = os.path.join(module.module_name, 'main.go')
    elif self.target_language == 'js':
      self.js_src = SourceFile()
      self.js_src.file_path = module.module_name + '.js'
      self.js_package = SourceFile()
      self.js_package.file_path = 'package.json'
      self.js_package.add_code('{\n  "type": "module"\n}\n')
    elif self.target_language == 'java':
      self.java_main_src = SourceFile()
      self.java_main_src.file_path = os.path.join(module.to_file_path(self.target_language), capitalize_first_letter(module.module_name) + '.java')
      self.java_class_srcs = []
    elif self.target_language == 'dotnet':
      self.csproj_src = SourceFile()
      self.csproj_src.file_path = os.path.join(module.to_file_path(self.target_language), 'headspace.csproj')
      self.csproj_src.add_code(DOTNET_CSPROJ_CONFIG)
      self.dotnet_main_src = SourceFile()
      self.dotnet_main_src.file_path = os.path.join(module.to_file_path(self.target_language), capitalize_first_letter(module.module_name) + '.cs')
      self.dotnet_class_srcs = []

  def convert_module_name(self):
    module_details = self.module_symbol_table.find_symbol('module')
    if not module_details:
      sys.exit('Unable to find a module ID.')
    # Different languages produce different filenames for a module.

  def emit_imports(self):
    if self.target_language == 'c':
      self.c_src.add_code('#include<stdlib.h>\n')
      self.c_src.add_code('#include<stdint.h>\n')
      self.c_src.add_code('#include<stdio.h>\n')
      self.c_src.add_code('\n')
      self.h_src.add_code('#include<stdlib.h>\n')
      self.c_src.add_code('#include<stdint.h>\n')
      self.h_src.add_code('\n')

  def indent(self, src, indent_level):
    if self.target_language == 'go':
      src.add_code('\t' * indent_level)
    else:
      src.add_code('  ' * indent_level)

  def emit_function_call(self, src, function_call_node, indent_level):
    function_identifier = function_call_node.members[0]
    if not function_identifier.node_type == 'ACCESS_CHAIN':
      sys.exit('Function call did not begin with an identifier chain.')
    is_print_function = False
    if function_identifier.members[0].members[0] == 'os':
      if function_identifier.members[1].members[0] == 'print':
        if self.target_language == 'c':
          src.add_code('printf')
        elif self.target_language == 'py':
          is_print_function = True
          src.add_code('print')
        elif self.target_language == 'go':
          if '"fmt"' not in self.required_imports:
            self.required_imports.append('"fmt"')
          src.add_code('fmt.Print')
        elif self.target_language == 'js':
          src.add_code('process.stdout.write')
        elif self.target_language == 'java':
          src.add_code('System.out.print')
        elif self.target_language == 'dotnet':
          src.add_code('Console.Write')
    function_args = function_call_node.members[1]
    src.add_code('(')
    for arg in function_args.members:
      if arg.node_type == 'STRING_LITERAL':
        src.add_code(arg.members[0])
    if is_print_function and self.target_language == 'py':
      src.add_code(', end=""')
    src.add_code(')')

  def emit_statement(self, src, statement_node, indent_level):
    self.indent(src, indent_level)
    if statement_node.node_type == 'FUNCTION_CALL':
      self.emit_function_call(src, statement_node, indent_level)
      if self.target_language == 'c' or self.target_language == 'js' or self.target_language == 'java' or self.target_language == 'dotnet':
        src.add_code(';\n')
      if self.target_language == 'py' or self.target_language == 'go':
        src.add_code('\n')
    else:
      print('Unexpected statement node:')
      statement_node.print()

  def emit_code_block(self, src, code_block, indent_level):
    if self.target_language == 'c' or self.target_language == 'go' or self.target_language == 'js' or self.target_language == 'java' or self.target_language == 'dotnet':
      self.indent(src, indent_level)
      src.add_code('{\n')
    elif self.target_language == 'py':
      self.indent(src, indent_level)
      src.add_code(':\n')
    for statement_node in code_block.members:
      member_indent = 1
      if self.target_language == 'java':
        member_indent = 2
      elif self.target_language == 'dotnet':
        member_indent = 3
      self.emit_statement(src, statement_node, indent_level + member_indent)
    if self.target_language == 'c' or self.target_language == 'go' or self.target_language == 'js' or self.target_language == 'java' or self.target_language == 'dotnet':
      if self.target_language == 'java':
        self.indent(src, indent_level + 1)
      elif self.target_language == 'dotnet':
        self.indent(src, indent_level + 2)
      else:
        self.indent(src, indent_level)
      src.add_code('}\n')
    elif self.target_language == 'py':
      src.add_code('\n')

  def emit_main(self):
    # The function signature for main can be found in the symbol table.
    if self.target_language == 'c':
      # TODO: support reading command line arguments.
      self.c_src.add_code('int main(void) ')
    elif self.target_language == 'py':
      self.py_src.add_code('def main()')
    elif self.target_language == 'go':
      self.go_main_src.add_code('func main() ')
    elif self.target_language == 'js':
      self.js_src.add_code('function main() ')
    elif self.target_language == 'java':
      module = self.module_symbol_table.symbols['module']
      self.java_main_src.add_code('package ' + module.to_namespace(self.target_language) + ';\n\n')
      self.java_main_src.add_code('public class ' + capitalize_first_letter(module.module_name) + '\n{\n')
      self.java_main_src.add_code('  public static void main(String[] args) ')
    elif self.target_language == 'dotnet':
      module = self.module_symbol_table.symbols['module']
      self.dotnet_main_src.add_code('using System;\n\n')
      self.dotnet_main_src.add_code('namespace ' + module.to_namespace(self.target_language) + ' {\n')
      self.dotnet_main_src.add_code('  class ' + capitalize_first_letter(module.module_name) + ' {\n')
      self.dotnet_main_src.add_code('    static void Main(string[] args) ')
    # Find the main method's code block in the parse tree.
    main_node = self.find_main_function_node()
    if not main_node:
      sys.exit('Main function node not found.')
    main_code_block = main_node.members[3]
    if self.target_language == 'c':
      self.emit_code_block(self.c_src, main_code_block, 0)
    elif self.target_language == 'py':
      self.emit_code_block(self.py_src, main_code_block, 0)
    elif self.target_language == 'go':
      self.emit_code_block(self.go_main_src, main_code_block, 0)
    elif self.target_language == 'js':
      self.emit_code_block(self.js_src, main_code_block, 0)
    elif self.target_language == 'java':
      self.emit_code_block(self.java_main_src, main_code_block, 0)
    elif self.target_language == 'dotnet':
      self.emit_code_block(self.dotnet_main_src, main_code_block, 0)
    if self.target_language == 'c':
      # In C, a return statement must be injected for the main function.
      self.c_src.parts.insert(-1, '  return 0;\n')
    elif self.target_language == 'py':
      self.py_src.add_code('if __name__ == "__main__":\n')
      self.py_src.add_code('  main()\n')
    elif self.target_language == 'go':
      # We need to prepend the imports for the go module, so that we can add
      # required imports after we see which methods are used.
      self.prepend_required_imports(self.go_main_src)
      # The package declaration for go needs to be at the top of the file,
      # so prepend it last.
      self.prepend_package(self.go_main_src, 'main')
    elif self.target_language == 'js':
      self.js_src.add_code('\nmain();\n')
    elif self.target_language == 'java':
      self.java_main_src.add_code('}\n')
    elif self.target_language == 'dotnet':
      self.dotnet_main_src.add_code('  }\n}\n')

  def prepend_required_imports(self, src):
    if self.target_language == 'go':
      if self.required_imports:
        src.parts.insert(0, '\n')
      for required_import in self.required_imports:
        src.parts.insert(0, 'import ' + required_import + '\n')

  def prepend_package(self, src, package_name):
    if self.target_language == 'go':
      src.parts.insert(0, '\n\n')
      src.parts.insert(0, 'package ' + package_name)

  def debug_node(self, debug_note, node=None):
    if self.debug_print:
      print(' ' * self.debug_indent, end='')
      print('| ', debug_note)
      if node is not None:
        node.print()

  def enter_method(self, debug_note):
    if self.debug_print:
      print(' ' * self.debug_indent, end='')
      print('/ converter entering ', debug_note)
      self.debug_indent += 4

  def leave_method(self, debug_note):
    if self.debug_print:
      self.debug_indent -= 4
      if self.debug_indent < 0:
        sys.exit('Enter and leave mismatch.')
      print(' ' * self.debug_indent, end='')
      print('\\ converter  leaving ', debug_note)


def convert(parse_tree, target_language, debug_print=False):
  converter = Converter(parse_tree, target_language, debug_print)
  return converter.emit_code()


def convert_filename(filename, target_language):
  with open(filename, 'r') as source_file:
    source_code = source_file.read()
  source_tree = parser.parse_source(source_code)
  results_files = convert(source_tree, target_language)
  for result_file in results_files:
    with open(result_file.filename, 'w') as output_file:
      output_file.write(result_file.content)

