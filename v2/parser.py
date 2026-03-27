
import sys

import lexer


# Parse tree checklist:
# function call - done
# nested function call
# function declaration - done
# foreign code block - done
# variable declaration
# conditional statement (if)
# loop statement (while)
# assigment statement - done
# module name - done
# return statement - done
# infix operators


INFIX_OPERATORS = ['+']


class Node:

  def __init__(self, node_type, members=None, leaf=False):
    self.node_type = node_type
    self.leaf = leaf
    self.members = members or []

  def print(self, indent_level=0):
    if self.leaf:
      print(' ' * indent_level, self.node_type, ':')
      for member in self.members:
        if self.node_type == 'SPACES':
          print(' ' * (indent_level + 2), '[', member, ']')
        else:
          print(' ' * (indent_level + 2), member)
    else:
      print(' ' * indent_level, self.node_type, ':')
      for member in self.members:
        member.print(indent_level + 2)


class Parser:

  def __init__(self, tokens):
    self._tokens = tokens
    self._tokens_len = len(tokens)
    self.index = 0
    self.debug_print = False

  def current_token(self):
    if self.index >= self._tokens_len:
      return None
    return self._tokens[self.index]

  def next_token(self, skip_count=1):
    if self.index + skip_count >= self._tokens_len:
      return None
    # Skip spaces when looking ahead to next token.
    elif self._tokens[self.index + skip_count].token_type == 'SPACE':
      return self.next_token(skip_count + 1)
    return self._tokens[self.index + skip_count]

  def consume_current_token(self, debug_note):
    if self.debug_print:
      current_token = self.current_token()
      if current_token and current_token.token_type != 'SPACE':
        print('    consumed:', debug_note)
        self.current_token().print()
    self.index += 1

  def process_whitespace(self, parent_node):
    # TODO: consider removing this in favor of skipping whitespace.
    current_token = self.current_token()
    if current_token and current_token.token_type == 'SPACE':
      whitespace_tokens = []
      whitespace_node = Node('SPACES')
      whitespace_node.leaf = True
      # Leave out whitespace from the parse tree.
      #parent_node.members.append(whitespace_node)
      while current_token and current_token.token_type == 'SPACE':
        # Leave out whitespace from the parse tree.
        #whitespace_node.members.append(current_token.content)
        self.consume_current_token('processed whitespace')
        current_token = self.current_token()

  def process_identifier_chain(self, parent_node):
    # Starts with an identifier, possibly followed by a . and another identifier.
    current_token = self.current_token()
    identifier_chain = Node('IDENTIFIER_CHAIN')
    if not current_token or not current_token.token_type == 'IDENTIFIER':
      print('Expected a chain of identifiers to start with an identifier')
      sys.exit(1)
    identifier_chain.members.append(Node('IDENTIFIER', [current_token.content], True))
    next_token = self.next_token()
    while next_token and next_token.matches('SYMBOL', '.'):
      # Add the . that comes after the identifier.
      self.consume_current_token('processed identifier in chain')
      current_token = self.current_token()
      identifier_chain.members.append(Node('MEMBER_DOT_ACCESS', [current_token.content], True))
      self.consume_current_token('processed dot in identifier chain')
      current_token = self.current_token()
      if not current_token or not current_token.token_type == 'IDENTIFIER':
        print('Expected a chain of identifiers to have an identifier following a . (dot)')
        sys.exit(1)
      identifier_chain.members.append(Node('IDENTIFIER', [current_token.content], True))
      next_token = self.next_token()
    self.consume_current_token('processed final identifier in chain')
    parent_node.members.append(identifier_chain)

  def process_argument_list(self, parent_node):
    current_token = self.current_token()
    argument_list = Node('ARGUMENTS')
    # TODO: consume tokens until reaching the closing ]
    if current_token:
      if current_token.token_type == 'STRING':
        argument_list.members.append(Node('STRING_LITERAL', [current_token.content], True))
        self.consume_current_token('processed string literal argument')
      elif current_token.token_type == 'NUMBER':
        argument_list.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
        self.consume_current_token('processed number literal argument')
      elif current_token.token_type == 'IDENTIFIER':
        # This may be an identifier chain or a function call. We can process it as an rvalue.
        self.process_rvalue(argument_list)
        # TODO: handle a function call.
    parent_node.members.append(argument_list)

  def process_function_call(self, parent_node):
    # Starts with an identifier followed by [.
    current_token = self.current_token()
    function_call = Node('FUNCTION_CALL_ARGUMENTS')
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a function call to have an opening [ after the identifier')
      sys.exit(1)
    function_call.members.append(Node('ARG_LIST_START', [current_token.content], True))
    self.consume_current_token('processed opening [ of arg list')
    self.process_whitespace(function_call)
    # After the opening block, get the list of all arguments.
    self.process_argument_list(function_call)
    self.process_whitespace(function_call)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', ']'):
      print('Expected a function call to have a closing ] after the function arguments')
      sys.exit(1)
    function_call.members.append(Node('ARG_LIST_END', [current_token.content], True))
    self.consume_current_token('processed closing ] of arg list')
    parent_node.members.append(function_call)

  def process_foreign_code_block(self, parent_node):
    # Current node is the marker for starting the foreign code block.
    foreign_code_block = Node('FOREIGN_CODE_BLOCK')
    current_token = self.current_token()
    source_code_block = Node('temp', [], True)
    foreign_code_block.members.append(source_code_block)
    if current_token and current_token.content == 'BEGIN_FOREIGN_CODE_C':
      source_code_block.node_type = 'C'
    elif current_token and current_token.content == 'BEGIN_FOREIGN_CODE_PYTHON':
      source_code_block.node_type = 'PYTHON'
    elif current_token and current_token.content == 'BEGIN_FOREIGN_CODE_GO':
      source_code_block.node_type = 'GO'
    elif current_token and current_token.content == 'BEGIN_FOREIGN_CODE_JAVA':
      source_code_block.node_type = 'JAVA'
    elif current_token and current_token.content == 'BEGIN_FOREIGN_CODE_JS':
      source_code_block.node_type = 'JS'
    elif current_token and current_token.content == 'BEGIN_FOREIGN_CODE_DOTNET':
      source_code_block.node_type = 'DOTNET'
    self.consume_current_token('processed foreign code start')
    current_token = self.current_token()
    while current_token and not current_token.content.startswith('END_FOREIGN_CODE_'):
      source_code_block.members.append(current_token.content)
      self.consume_current_token('processed foreign code token')
      current_token = self.current_token()
    if current_token and current_token.content.startswith('END_FOREIGN_CODE_'):
      # We have reached the end of the code block, consume this token and move forward.
      self.consume_current_token('processed foreign code end')
    parent_node.members.append(foreign_code_block)

  def process_infix_operation(self, parent_node):
    infix_operation = Node('INFIX_OPERATION')
    current_token = self.current_token()
    if current_token and current_token.token_type == 'STRING':
      # Move past the first operand.
      infix_operation.members.append(Node('STRING_LITERAL', [current_token.content], True))
      self.consume_current_token('processed first string operand in infix')
    elif current_token and current_token.token_type == 'NUMBER':
      # Move past the first operand.
      infix_operation.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
      self.consume_current_token('processed first number operand in infix')
    elif current_token and current_token.token_type == 'IDENTIFIER':
      self.process_identifier_chain(infix_operation)
    self.process_whitespace(infix_operation)
    current_token = self.current_token()
    if current_token and current_token.token_type != 'SYMBOL':
      print('In an infix operation, the symbol should follow the first operand.')
      sys.exit(1)
    if current_token and current_token.token_type == 'SYMBOL' and current_token.content in INFIX_OPERATORS:
      infix_operation.members.append(Node('OPERATOR', [current_token.content], True))
    # Move past the operator.
    self.consume_current_token('processed infix operator')
    self.process_whitespace(infix_operation)
    # TODO: For the second operand in the operation, process an rvalue. This allows chaining.
    current_token = self.current_token()
    if not current_token:
      print('In an infix operation, there should be a second operand after the operator.')
      sys.exit(1)
    if current_token and current_token.token_type == 'STRING':
      # Move past the first operand.
      infix_operation.members.append(Node('STRING_LITERAL', [current_token.content], True))
      self.consume_current_token('processed first string operand in infix')
    elif current_token and current_token.token_type == 'NUMBER':
      # Move past the first operand.
      infix_operation.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
      self.consume_current_token('processed first number operand in infix')
    elif current_token and current_token.token_type == 'IDENTIFIER':
      self.process_identifier_chain(infix_operation)
    parent_node.members.append(infix_operation)

  def process_rvalue(self, parent_node):
    current_token = self.current_token()
    # Lookahead to see if there is a symbol for an infix operation.
    next_token = self.next_token()
    if next_token and next_token.token_type == 'SYMBOL' and next_token.content in INFIX_OPERATORS:
      self.process_infix_operation(parent_node)
      self.process_whitespace(parent_node)
    elif current_token and current_token.token_type == 'STRING':
      parent_node.members.append(Node('STRING_LITERAL', [current_token.content], True))
      self.consume_current_token('processed string rvalue')
    elif current_token and current_token.token_type == 'NUMBER':
      parent_node.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
      self.consume_current_token('processed number rvalue')
    elif current_token and current_token.token_type == 'IDENTIFIER':
      sub_node = Node('temp')
      self.process_identifier_chain(sub_node)
      current_token = self.current_token()
      if current_token and current_token.matches('SYMBOL', '['):
        # This is a function/method call.
        self.process_function_call(sub_node)
        sub_node.node_type = 'FUNCTION_CALL'
        parent_node.members.append(sub_node)
      else:
        # This is just an identifier chain so add the chain directly.
        parent_node.members.append(sub_node.members[0])
    self.process_whitespace(parent_node)

  def process_assignment(self, parent_node):
    current_token = self.current_token()
    # First version: assignment starts with an identifier.
    assignment = Node('ASSIGNMENT')
    if not current_token or current_token.token_type != 'IDENTIFIER':
      print('Expected assignment to start with an identifier')
      sys.exit(1)
    assignment.members.append(Node('ASSIGNMENT_TARGET', [current_token.content], True))
    self.consume_current_token('processed assignment identifier')
    self.process_whitespace(assignment)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', '='):
      print('Expected assignment to have a = after the identifier')
      sys.exit(1)
    assignment.members.append(Node('ASSIGNMENT_SYMBOL', [current_token.content], True))
    self.consume_current_token('processed assignment symbol')
    self.process_whitespace(assignment)
    self.process_rvalue(assignment)
    parent_node.members.append(assignment)

  def process_return_statement(self, parent_node):
    current_token = self.current_token()
    return_statement = Node('RETURN_STATEMENT')
    if not current_token or not current_token.matches('IDENTIFIER', 'return'):
      print('Expected a return statement to start with return')
      sys.exit(1)
    self.consume_current_token('processed return identifier')
    self.process_whitespace(return_statement)
    self.process_rvalue(return_statement)
    parent_node.members.append(return_statement)

  def process_code_block(self, parent_node):
    current_token = self.current_token()
    # We expect the code block to start with an opening [.
    code_block = Node('CODE_BLOCK')
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a [ to begin a code block')
      sys.exit(1)
    code_block.members.append(Node('CODE_BLOCK_START', [current_token.content], True))
    self.consume_current_token('processed code block opening [')
    self.process_whitespace(code_block)
    current_token = self.current_token()
    while current_token and current_token.token_type == 'IDENTIFIER':
      if current_token.content.startswith('BEGIN_FOREIGN_CODE_'):
        self.process_foreign_code_block(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif current_token.content == 'return':
        self.process_return_statement(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      else:
        sub_node = Node('temp')
        self.process_whitespace(sub_node)
        self.process_identifier_chain(sub_node)
        self.process_whitespace(sub_node)
        current_token = self.current_token()
        if current_token and current_token.matches('SYMBOL', '['):
          # This is a function/method call.
          self.process_function_call(sub_node)
          sub_node.node_type = 'FUNCTION_CALL'
          code_block.members.append(sub_node)
        self.process_whitespace(sub_node)
        current_token = self.current_token()
    self.process_whitespace(code_block)
    current_token = self.current_token()
    if current_token and current_token.matches('SYMBOL', ']'):
      code_block.members.append(Node('CODE_BLOCK_END', [current_token.content], True))
    parent_node.members.append(code_block)

  def process_parameters_list(self, parent_node):
    parameters_list = Node('PARAMETERS_LIST')
    processing_parameters = True
    while processing_parameters:
      current_token = self.current_token()
      declaration_tree = Node('DECLARATION')
      self.process_whitespace(declaration_tree)
      declaration_tree.members.append(Node('IDENTIFIER', [current_token.content], True))
      self.consume_current_token('processed declared identifier parameter')
      self.process_whitespace(declaration_tree)
      current_token = self.current_token()
      if current_token and current_token.matches('SYMBOL', ':'):
        declaration_tree.members.append(Node('DECLARATION_MARKER', [':'], True))
      else:
        print('Expected : after variable name in declaration')
        sys.exit(1)
      self.consume_current_token('processed type marker in parameter declaration')
      self.process_whitespace(declaration_tree)
      current_token = self.current_token()
      if current_token and current_token.matches('IDENTIFIER', 'function'):
        # Can't decalre a function in a parameters list.
        print('A function cannot be declared in a list of paramters.')
        sys.exit(1)
      else:
        # This is a variable declaration, use this identifier as the type.
        declaration_tree.members.append(Node('VARIABLE_TYPE', [current_token.content], True))
        self.consume_current_token('processed type identifier in parameter declaration')
      parameters_list.members.append(declaration_tree)
      self.process_whitespace(declaration_tree)
      current_token = self.current_token()
      if current_token and current_token.matches('SYMBOL', ','):
        processing_parameters = True
        # Consume the comma seperator and move to the next.
        self.consume_current_token('processed parameter separator in parameters list')
      else:
        processing_parameters = False
    parent_node.members.append(declaration_tree)


  def process_function_definition(self, parent_node):
    current_token = self.current_token()
    # The current token is the identifier 'function' to begin the declaration.
    function_definition = Node('FUNCTION_DEFINITION')
    if not current_token or not current_token.matches('IDENTIFIER', 'function'):
      print('function definition did not begin with keyword function')
      sys.exit(1)
    function_definition.members.append(Node('FUNCTION_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed function keyword in function declaration')
    self.process_whitespace(function_definition)
    current_token = self.current_token()
    # Should be an opening [ for the parameter list.
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a [ after the function keyword in function definition')
      sys.exit(1)
    function_definition.members.append(Node('FUNCTION_PARAMS_START', [current_token.content], True))
    self.consume_current_token('processed opening [ in function parameters list')
    self.process_whitespace(function_definition)
    current_token = self.current_token()
    # TODO: process the list of parameter declarations.
    if current_token and current_token.token_type == 'IDENTIFIER':
      self.process_parameters_list(function_definition)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', ']'):
      print('Expected a ] after the first [ in a function definition')
      sys.exit(1)
    function_definition.members.append(Node('FUNCTION_PARAMS_END', [current_token.content], True))
    self.consume_current_token('processed closing ] in function parameter list')
    self.process_whitespace(function_definition)
    self.process_code_block(function_definition)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', ']'):
      print('Expected a ] after the first [ in a function definition')
      sys.exit(1)
    parent_node.members.append(function_definition)
    self.consume_current_token('processing closing ] in function declaration')

  def process_declaration(self, parent_node):
    current_token = self.current_token()
    declaration_tree = Node('DECLARATION')
    self.process_whitespace(declaration_tree)
    declaration_tree.members.append(Node('IDENTIFIER', [current_token.content], True))
    self.consume_current_token('processed starting identifier in declaration')
    self.process_whitespace(declaration_tree)
    current_token = self.current_token()
    if current_token and current_token.matches('SYMBOL', ':'):
      declaration_tree.members.append(Node('DECLARATION_MARKER', [':'], True))
    else:
      print('Expected : after variable name in declaration')
      sys.exit(1)
    self.consume_current_token('processed type separator in declaration')
    self.process_whitespace(declaration_tree)
    current_token = self.current_token()
    if current_token and current_token.matches('IDENTIFIER', 'function'):
      # This is a function declaration.
      declaration_tree.node_type = 'FUNCTION_DECLARATION'
      self.process_function_definition(declaration_tree)
    else:
      # This is a variable declaration, use this identifier as the type.
      declaration_tree.members.append(Node('VARIABLE_TYPE', [current_token.content], True))
      self.consume_current_token('processed variable type identifier in declaration')
    parent_node.members.append(declaration_tree)


  def build_parse_tree(self):
    top_node = Node('MODULE')
    if not self._tokens or self._tokens_len == 0:
      return None
    # Consume any leading whitespace.
    self.process_whitespace(top_node)
    current_token = self.current_token()
    while current_token and current_token.token_type == 'IDENTIFIER':
      # This could be a variable/function declaration, an execution statement, etc.
      next_token = self.next_token()
      if next_token and next_token.token_type == 'SYMBOL':
        # Check the next token for a : which would make this a declaration.
        if next_token.content == ':':
          # This is a declaration.
          self.process_declaration(top_node)
        elif next_token.content == '=':
          self.process_assignment(top_node)
        elif next_token.content == '+':
          self.process_infix_operation(top_node)
      current_token = self.current_token()
      if current_token:
        self.process_whitespace(top_node)
      current_token = self.current_token()
    return top_node


def parse_tokens(tokens, debug_print=False):
  parser = Parser(tokens)
  parser.debug_print = debug_print
  return parser.build_parse_tree()


def parse_source(source_code, debug_print=False):
  return parse_tokens(lexer.tokenize(source_code), debug_print)

