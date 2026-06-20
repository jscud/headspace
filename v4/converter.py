import parser
import sys
import os


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


class Converter:

  def __init__(self, parse_tree, target_language, debug_print=False):
    self.tree = parse_tree
    self.module_symbol_table = SymbolTable()
    self.target_language = target_language
    self.debug_print = debug_print
    self.debug_indent = 0
    # Language specific source files to append to as the parse tree is
    # converted.
    self.c_src = None
    self.h_src = None

  def emit_code(self):
    # Start by populating symbols in the module.
    self.populate_symbols()
    self.populate_source_files()
    if self.has_main_function():
      pass
    if self.target_language == 'c':
      return [self.c_src, self.h_src]
    else:
      return []

  def extract_type(self, type_chain_node):
    type_parts = []
    if type_chain_node.node_type != 'TYPE_CHAIN':
      sys.exit('Expected to extract the type from a type chain node')
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

  def convert_module_name(self):
    module_details = self.module_symbol_table.find_symbol('module')
    if not module_details:
      sys.exit('Unable to find a module ID.')
    # Different languages produce different filenames for a module.

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
        print('error, enter and leave mismatch')
        sys.exit(1)
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

