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
        sys.exit('error, enter and leave mismatch')
      print(' ' * self.debug_indent, end='')
      print('\\ parser  leaving ', debug_note, 'with debug level', self.debug_indent)

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
    self.enter_method('process_parameter_declaration')
    parameter_declaration = build_node('PARAMETER')
    if not self.current_token_matches('IDENTIFIER', 'param'):
      sys.exit('Expected parameter declaration to start with keyword param')
    self.consume_current_token('param keyword in parameter declaration')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected parameter declaration to have an identifier following the param keyword')
    parameter_declaration.members.append(build_leaf('PARAMETER_NAME', self.current_token().content))
    self.consume_current_token('parameter name')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected paraemter type to be present after the parameter name')
    parameter_declaration.members.append(self.process_type_chain())
    self.leave_method('process_parameter_declaration')
    return parameter_declaration

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
    elif self.current_token_is('NUMBER'):
      expression_node = build_leaf('NUMBER_LITERAL', self.current_token().content)
      self.consume_current_token('number literal in lvalue expression')
    elif self.current_token_is('IDENTIFIER'):
      chain = self.process_access_chain()
      if self.current_token_matches('SYMBOL', '('):
        # This is a function call.
        expression_node = self.process_function_call(chain)
      else:
        # It is simply the identifier, so return it.
        expression_node = chain
      # TODO: more types?
    else:
      self.current_token().print()
      sys.exit('unexpected token')
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

  def process_return_statement(self):
    self.enter_method('process_return_statment')
    return_statement = build_node('RETURN_STATEMENT')
    if not self.current_token_matches('IDENTIFIER', 'return'):
      sys.exit('Expected return statement to start with keyword return')
    self.consume_current_token('return keyword')
    return_statement.members.append(self.process_lvalue_expression())
    self.leave_method('process_return_statment')
    return return_statement

  def process_member_declaration(self):
    self.enter_method('process_member_declaration')
    member_declaration = build_node('MEMBER_DECLARATION')
    if not self.current_token_matches('IDENTIFIER', 'member'):
      sys.exit('Expected member declaration to start with keyword member')
    self.consume_current_token('member keyword in class declaration')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected member declaration to have an identifier following the member keyword')
    member_declaration.members.append(build_leaf('MEMBER_NAME', self.current_token().content))
    self.consume_current_token('member name')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected paraemter type to be present after the parameter name')
    member_declaration.members.append(self.process_type_chain())
    self.leave_method('process_member_declaration')
    return member_declaration

  def process_constructor_declaration(self):
    self.enter_method('process_constructor_declaration')
    constructor_declaration = build_node('CONSTRUCTOR_DEFINITION')
    if not self.current_token_matches('IDENTIFIER', 'constructor'):
      sys.exit('Expected constuctor declaration to start with keyword constructor')
    self.consume_current_token('constructor keyword in class declaration')
    constructor_declaration.members.append(self.process_parameter_declarations())
    constructor_declaration.members.append(self.process_code_block())
    self.leave_method('process_constructor_declaration')
    return constructor_declaration

  def process_assignment_statement(self):
    self.enter_method('process_assignment_statement')
    assignment_statement = build_node('ASSIGNMENT_STATEMENT')
    if not self.current_token_matches('IDENTIFIER', 'set'):
      sys.exit('Expected assignment statement to start with keyword set')
    self.consume_current_token('set keyword in assignment statement')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected assignment statement to begin with target identifier')
    chain = self.process_access_chain()
    assignment_target = build_node('ASSIGNMENT_TARGET')
    assignment_target.members.append(chain)
    assignment_statement.members.append(assignment_target)
    if not self.current_token_matches('SYMBOL', '='):
      sys.exit('Expected assignment statement to include = symbol')
    self.consume_current_token('= symbol in assignment statement')
    assignment_target = build_node('ASSIGNMENT_TARGET')
    assignment_target.members.append(self.process_lvalue_expression())
    assignment_statement.members.append(assignment_target)
    self.leave_method('process_assignment_statement')
    return assignment_statement

  def process_code_block(self):
    self.enter_method('process_code_block')
    code_block = build_node('CODE_BLOCK')
    if not self.current_token_matches('SYMBOL', '{'):
      sys.exit('Expected code block to start with an opening {')
    self.consume_current_token('opening { in code block')

    while self.current_token_is('IDENTIFIER'):
      if self.current_token_matches('IDENTIFIER', 'BEGIN_FOREIGN_CODE'):
        code_block.members.append(self.process_foreign_code())
      elif self.current_token_matches('IDENTIFIER', 'return'):
        code_block.members.append(self.process_return_statement())
      elif self.current_token_matches('IDENTIFIER', 'member'):
        code_block.members.append(self.process_member_declaration())
      elif self.current_token_matches('IDENTIFIER', 'constructor'):
        code_block.members.append(self.process_constructor_declaration())
      elif self.current_token_matches('IDENTIFIER', 'set'):
        code_block.members.append(self.process_assignment_statement())
      elif self.current_token_matches('IDENTIFIER', 'method'):
        code_block.members.append(self.process_method_declaration())
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
      sys.exit('Expected function declaration to have a string literal following the function keyword')
    function_declaration.members.append(build_leaf('FUNCTION_NAME', self.current_token().content))
    self.consume_current_token('function name')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected function return type to be present after the function name')
    function_declaration.members.append(self.process_type_chain())
    function_declaration.members.append(self.process_parameter_declarations())
    function_declaration.members.append(self.process_code_block())
    self.leave_method('process_function_declaration')
    return function_declaration

  def process_method_declaration(self):
    self.enter_method('process_method_declaration')
    method_declaration = build_node('METHOD_DECLARATION')
    if not self.current_token_matches('IDENTIFIER', 'method'):
      sys.exit('Expected method declaration to start with method keyword')
    self.consume_current_token('method keyword')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected method declaration to have a string literal following the method keyword')
    method_declaration.members.append(build_leaf('METHOD_NAME', self.current_token().content))
    self.consume_current_token('method name')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected method return type to be present after the method name')
    method_declaration.members.append(self.process_type_chain())
    method_declaration.members.append(self.process_parameter_declarations())
    method_declaration.members.append(self.process_code_block())
    self.leave_method('process_method_declaration')
    return method_declaration

  def process_class_declaration(self):
    self.enter_method('process_class_declaration')
    class_declaration = build_node('CLASS_DECLARATION')
    if not self.current_token_matches('IDENTIFIER', 'class'):
      sys.exit('Expected class declaration to start with class keyword')
    self.consume_current_token('class keyword')
    if not self.current_token_is('IDENTIFIER'):
      sys.exit('Expected class declaration to have a string literal following the class keyword')
    class_declaration.members.append(build_leaf('CLASS_NAME', self.current_token().content))
    self.consume_current_token('class name')
    class_declaration.members.append(self.process_code_block())
    self.leave_method('process_class_declaration')
    return class_declaration

  def process_module_node(self):
    self.enter_method('process_module_node')
    module_node = None
    if self.current_token_matches('IDENTIFIER', 'module'):
      module_node = self.process_module_declaration()
    elif self.current_token_matches('IDENTIFIER', 'function'):
      module_node = self.process_function_declaration()
    elif self.current_token_matches('IDENTIFIER', 'BEGIN_FOREIGN_CODE'):
      module_node = self.process_foreign_code()
    elif self.current_token_matches('IDENTIFIER', 'class'):
      module_node = self.process_class_declaration()
    self.leave_method('process_module_node')
    return module_node

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


