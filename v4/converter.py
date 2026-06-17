import parser
import sys
import os


class SourceFile:

  def __init__(self):
    self.file_path = ''
    self.content = ''


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

  # Note that when a module is imported, it should be parsed and its symbol table populated.


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

  def emit_code(self):
    # Start by populating symbols in the module.
    self.populate_symbols()
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

