import lexer
import sys


class Node:

  def __init__(self, node_type, members=None, leaf=False):
    self.node_type = node_type
    self.leaf = leaf
    self.members = members or []

  def print(self, indent_level=0):
    print(self.dump(indent_level))

  def dump(self, indent_level=0):
    output = []
    if self.leaf:
      output.append(' ' * indent_level + self.node_type + ':')
      for member in self.members:
        if self.node_type == 'SPACES':
          output.append(' ' * (indent_level + 2) + '[' + member + ']')
        else:
          output.append(' ' * (indent_level + 2) + member)
    else:
      output.append(' ' * indent_level + self.node_type + ':')
      for member in self.members:
        output.append(member.dump(indent_level + 2))
    return '\n'.join(output)


def build_node(node_type):
  return Node(node_type)


def build_leaf(node_type, node_value):
  return Node(node_type, [node_value], True)


class Parser:

  def __init__(self, tokens):
    self._tokens = tokens
    self._tokens_len = len(tokens)
    self.index = 0
    self.debug_print = False
    self.debug_indent = 0

  def current_token(self, skip_whitespace=True):
    if skip_whitespace:
      while self.index < self._tokens_len and self._tokens[self.index].token_type == 'SPACE':
        self.index += 1
    if self.index >= self._tokens_len:
      return None
    return self._tokens[self.index]

  def current_token_is(self, token_type):
    token = self.current_token()
    return token is not None and token.token_type == token_type

  def current_token_matches(self, token_type, exact_value):
    token = self.current_token()
    return token is not None and token.matches(token_type, exact_value)

  def next_token(self, skip_count=1):
    if self.index + skip_count >= self._tokens_len:
      return None
    # Skip spaces when looking ahead to next token.
    elif self._tokens[self.index + skip_count].token_type == 'SPACE':
      return self.next_token(skip_count + 1)
    return self._tokens[self.index + skip_count]

  def next_token_is(self, token_type):
    token = self.next_token()
    return token is not None and token.token_type == token_type

  def next_token_matches(self, token_type, exact_value):
    token = self.next_token()
    return token is not None and token.matches(token_type, exact_value)

  def consume_current_token(self, debug_note, skip_whitespace=True):
    if self.debug_print:
      current_token = self.current_token(skip_whitespace)
      print(' ' * self.debug_indent, end='')
      print('consumed@', debug_note)
      print(' ' * (self.debug_indent + 2), end='')
      current_token.print()
    self.index += 1

  def enter_method(self, debug_note):
    if self.debug_print:
      print(' ' * self.debug_indent, end='')
      print('/ parser entering ', debug_note)
      self.debug_indent += 4

  def leave_method(self, debug_note):
    if self.debug_print:
      self.debug_indent -= 4
      if self.debug_indent < 0:
        print('error, enter and leave mismatch')
        sys.exit(1)
      print(' ' * self.debug_indent, end='')
      print('\\ parser  leaving ', debug_note)

  # Tricky question, I need to process identifier chain, it includes things like list access []
  def process_access_chain(self):
    self.enter_method('process_access_chain')
    chain = build_node('ACCESS_CHAIN')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected access chain to start with an identifier')
    chain.members.append(build_leaf('INITIAL_IDENTIFIER', self.current_token().content))
    self.consume_current_token('first identifier in chain')
    check_for_next_item = True
    while check_for_next_item:
      if self.current_token_matches('SYMBOL', '.'):
        # This has a sub item.
        self.consume_current_token('dot in member chain')
        if not self.current_token_is('IDENTIFIER'):
          sys.exit('Expected access chain to have an identifier following . operator')
        chain.members.append(build_leaf('CHAINED_IDENTIFIER', self.current_token().content))
        self.consume_current_token('additional identifier in member chain')
      elif self.current_token_matches('SYMBOL', '['):
        # This is a collection member access.
        # TODO: implement this, remember that the member access is an lvalue expression.
        pass
      else:
        # The chain has ended.
        check_for_next_item = False
    self.leave_method('process_access_chain')
    return chain

  def process_type_chain(self):
    self.enter_method('process_type_chain')
    chain = build_node('TYPE_CHAIN')
    if not self.current_token_matches('IDENTIFIER', 'type'):
      sys.exit('Expected type chain to start with the type keyword')
    self.consume_current_token('type keyword')
    if not self.current_token_matches('SYMBOL', '.'):
      sys.exit('Expected type chain to have a dot following the type keyword')
    self.consume_current_token('dot following type keyword')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected type chain to start with an identifier after the type keyword')
    chain.members.append(build_leaf('INITIAL_TYPE', self.current_token().content))
    self.consume_current_token('initial type identifier')
    check_for_next_item = True
    while check_for_next_item:
      if self.current_token_matches('SYMBOL', '.'):
        # This has a sub type.
        self.consume_current_token('dot in type chain')
        if not self.current_token_is('IDENTIFIER'):
          sys.exit('Expected type chain to have an identifier following . operator')
        chain.members.append(build_leaf('CHAINED_IDENTIFIER', self.current_token().content))
        self.consume_current_token('additional identifier in type chain')
      else:
        # The chain has ended.
        check_for_next_item = False
    self.leave_method('process_type_chain')
    return chain

  def process_module_declaration(self):
    self.enter_method('process_module_declaration')
    if not self.current_token_matches('IDENTIFIER', 'module'):
      sys.exit('Expected module declaration to start with module keyword')
    self.consume_current_token('module keyword')
    if not self.current_token_is('STRING'):
      sys.exit('Expected module declaration to have a string literal following the module keyword')
    module_id = build_leaf('MODULE_ID', self.current_token().content)
    self.consume_current_token('module id value')
    self.leave_method('process_module_declaration')
    return module_id

  def process_parameter_declaration(self):
    return None

  def process_parameter_declarations(self):
    self.enter_method('process_parameter_declarations')
    parameters = build_node('PARAMETER_DECLARATIONS')
    if not self.current_token_matches('SYMBOL', '('):
      sys.exit('Expected parameter declarations to start with an opening (')
    self.consume_current_token('opening ( in parameter declarations')
    while self.current_token() is not None and not self.current_token_matches('SYMBOL', ')'):
      parameter = self.process_parameter_declaration()
      if parameter is not None:
        parameters.members.append(parameter)
      if self.current_token_matches('SYMBOL', ','):
        self.consume_current_token('seperator , in parameter declarations')
    if not self.current_token_matches('SYMBOL', ')'):
      sys.exit('Expected parameter declarations to end with a closing )')
    self.consume_current_token('closing ) in parameter declarations')
    self.leave_method('process_parameter_declarations')
    return parameters

  def process_lvalue_expression(self):
    self.enter_method('process_lvalue_expression')
    expression_node = None
    if self.current_token_is('STRING'):
      expression_node = build_leaf('STRING_LITERAL', self.current_token().content)
      self.consume_current_token('string literal in lvalue expression')
    self.leave_method('process_lvalue_expression')
    return expression_node

  def process_function_call(self, identifier_chain):
    self.enter_method('process_function_call')
    function_call = build_node('FUNCTION_CALL')
    function_call.members.append(identifier_chain)
    if not self.current_token_matches('SYMBOL', '('):
      sys.exit('Expected function call to start with an opening (')
    self.consume_current_token('opening ( in function call')
    args = build_node('ARGUMENTS_LIST')
    while self.current_token() is not None and not self.current_token_matches('SYMBOL', ')'):
      arg_expression = self.process_lvalue_expression()
      if arg_expression:
        args.members.append(arg_expression)
      if self.current_token() and self.current_token_matches('SYMBOL', ','):
        self.consume_current_token('seperator , between function call arguments')
    if not self.current_token_matches('SYMBOL', ')'):
      sys.exit('Expected function call to end with cloding )')
    self.consume_current_token('closing ) in function call')
    function_call.members.append(args)
    self.leave_method('process_function_call')
    return function_call

  def process_foreign_code(self):
    self.enter_method('process_foreign_code')
    if not self.current_token_matches('IDENTIFIER', 'BEGIN_FOREIGN_CODE'):
      sys.exit('Expected foreign code to start with marker BEGIN_FOREIGN_CODE')
    foreign_code = build_node('FOREIGN_CODE')
    self.consume_current_token('marker to begin foreign code')
    if not self.current_token_matches('SYMBOL', ':'):
      sys.exit('Expected foreign code to be followed by : before language')
    self.consume_current_token('foreign code language seperator')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected foreign code language to follow : seperator')
    foreign_code.members.append(build_leaf('TARGET_LANGUAGE', self.current_token().content))
    self.consume_current_token('foreign code target language')
    foreign_code_tokens = build_node('TOKENS')
    # Append all of the tokens as foreign code until we see the stop identifier.
    # Note that in foreign code, we do not skip spaces but pass them through.
    while self.current_token(skip_whitespace=False) and not self.current_token(skip_whitespace=False).matches('IDENTIFIER', 'END_FOREIGN_CODE'):
      foreign_code_tokens.members.append(build_leaf('FOREIGN_TOKEN', self.current_token(skip_whitespace=False).content))
      self.consume_current_token('foreign token', skip_whitespace=False)
    if not self.current_token_matches('IDENTIFIER', 'END_FOREIGN_CODE'):
      sys.exit('Expected foreign code to end with marker END_FOREIGN_CODE')
    self.consume_current_token('marker to end foreign code')
    foreign_code.members.append(foreign_code_tokens)
    self.leave_method('process_foreign_code')
    return foreign_code

  def process_code_block(self):
    self.enter_method('process_code_block')
    code_block = build_node('CODE_BLOCK')
    if not self.current_token_matches('SYMBOL', '{'):
      sys.exit('Expected code block to start with an opening {')
    self.consume_current_token('opening { in code block')

    while self.current_token_is('IDENTIFIER'):
      if self.current_token_matches('IDENTIFIER', 'BEGIN_FOREIGN_CODE'):
        code_block.members.append(self.process_foreign_code())
      else:
        chain = self.process_access_chain()
        if self.current_token_matches('SYMBOL', '('):
          # This is a function call.
          code_block.members.append(self.process_function_call(chain))

    if not self.current_token_matches('SYMBOL', '}'):
      sys.exit('Expected code block to end with a closing }')
    self.consume_current_token('closing } in code block')
    self.leave_method('process_code_block')
    return code_block

  def process_function_declaration(self):
    self.enter_method('process_function_declaration')
    function_declaration = build_node('FUNCTION_DECLARATION')
    if not self.current_token_matches('IDENTIFIER', 'function'):
      sys.exit('Expected function declaration to start with function keyword')
    self.consume_current_token('function keyword')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected module declaration to have a string literal following the module keyword')
    function_declaration.members.append(build_leaf('FUNCTION_NAME', self.current_token().content))
    self.consume_current_token('function name')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected function return type to be present after the function name')
    function_declaration.members.append(self.process_type_chain())
    function_declaration.members.append(self.process_parameter_declarations())
    function_declaration.members.append(self.process_code_block())
    self.leave_method('process_function_declaration')
    return function_declaration

  def process_module_node(self):
    self.enter_method('process_module_node')
    if self.current_token_matches('IDENTIFIER', 'module'):
      return self.process_module_declaration()
    elif self.current_token_matches('IDENTIFIER', 'function'):
      return self.process_function_declaration()
    elif self.current_token_matches('IDENTIFIER', 'BEGIN_FOREIGN_CODE'):
      return self.process_foreign_code()
    self.leave_method('process_module_node')
    return None

  def build_module(self):
    module_node = build_node('MODULE')
    if not self._tokens or self._tokens_len == 0:
      return None
    # Get all of the top level nodes in the module.
    child_node = self.process_module_node()
    while child_node:
      module_node.members.append(child_node)
      child_node = self.process_module_node()
    return module_node


def parse_tokens(tokens, debug_print=False):
  parser = Parser(tokens)
  parser.debug_print = debug_print
  return parser.build_module()


def parse_source(source_code, debug_print=False):
  return parse_tokens(lexer.tokenize(source_code), debug_print)


