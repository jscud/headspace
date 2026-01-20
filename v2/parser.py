
import sys

import lexer


# Parse tree checklist:
# function call
# function declaration


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

  def process_whitespace(self, parent_node):
    # TODO: consider removing this in favor of skipping whitespace.
    current_token = self.current_token()
    if current_token.token_type == 'SPACE':
      whitespace_tokens = []
      whitespace_node = Node('SPACES')
      whitespace_node.leaf = True
      parent_node.members.append(whitespace_node)
      while current_token and current_token.token_type == 'SPACE':
        whitespace_node.members.append(current_token.content)
        self.index += 1
        current_token = self.current_token()

  def process_function_call(self, parent_node):
    # Starts with an identifier followed by [.
    pass
    

  def process_code_block(self, parent_node):
    current_token = self.current_token()
    # We expect the code block to start with an opening [.
    code_block = Node('CODE_BLOCK')
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a [ to begin a code block')
      sys.exit(1)
    code_block.members.append(Node('SYMBOL', [current_token.content], True))
    self.index += 1
    self.process_whitespace(code_block)
    current_token = self.current_token()
    if current_token and current_token.token_type == 'IDENTIFIER':
      next_token = self.next_token()
      if next_token and next_token.matches('SYMBOL', '['):
        # This is a function/method call.
        self.process_function_call(code_block)
    parent_node.members.append(code_block)

  def process_function_definition(self, parent_node):
    current_token = self.current_token()
    # The current token is the identifier 'function' to begin the declaration.
    function_definition = Node('FUNCTION_DEFINITION')
    if not current_token or not current_token.matches('IDENTIFIER', 'function'):
      print('function definition did not begin with keyword function')
      sys.exit(1)
    function_definition.members.append(Node('FUNCTION_KEYWORD', [current_token.content], True))
    self.index += 1
    self.process_whitespace(function_definition)
    current_token = self.current_token()
    # Should be an opening [ for the parameter list.
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a [ after the function keyword in function definition')
      sys.exit(1)
    function_definition.members.append(Node('SYMBOL', [current_token.content], True))
    self.index += 1
    self.process_whitespace(function_definition)
    # TODO: process the list of parameter declarations.
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', ']'):
      print('Expected a ] after the first [ in a function definition')
      sys.exit(1)
    function_definition.members.append(Node('SYMBOL', [current_token.content], True))
    self.index += 1
    self.process_whitespace(function_definition)
    self.process_code_block(function_definition) 
    parent_node.members.append(function_definition)

  def process_declaration(self, parent_node):
    current_token = self.current_token()
    declaration_tree = Node('DECLARATION')
    self.process_whitespace(declaration_tree)
    declaration_tree.members.append(Node('IDENTIFIER', [current_token.content], True))
    self.index += 1
    self.process_whitespace(declaration_tree)
    current_token = self.current_token()
    if current_token and current_token.matches('SYMBOL', ':'):
      declaration_tree.members.append(Node('SYMBOL', [':'], True))
    else:
      print('Expected : after variable name in declaration')
      sys.exit(1)
    self.index += 1
    self.process_whitespace(declaration_tree)
    current_token = self.current_token()
    if current_token and current_token.matches('IDENTIFIER', 'function'):
      # This is a function declaration.
      self.process_function_definition(declaration_tree)
    else:
      # This is a variable declaration, use this identifier as the type.
      declaration_tree.members.append(Node('VARIABLE_TYPE', [current_token.content], True))
      self.index += 1
    parent_node.members.append(declaration_tree)

  def build_parse_tree(self):
    top_node = Node('MODULE')
    if not self._tokens or self._tokens_len == 0:
      return None
    # Consume any leading whitespace.
    self.process_whitespace(top_node)
    current_token = self.current_token()
    if current_token and current_token.token_type == 'IDENTIFIER':
      # This could be a variable/function declaration, an execution statement, etc.
      next_token = self.next_token()
      if next_token and next_token.token_type == 'SYMBOL':
        # Check the next token for a : which would make this a declaration.
        if next_token.content == ':':
          # This is a declaration.
          self.process_declaration(top_node)
    return top_node
    

def parse_tokens(tokens):
  parser = Parser(tokens)
  return parser.build_parse_tree()


def parse_source(source_code):
  return parse_tokens(lexer.tokenize(source_code))

