
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
    self.current_node = None

  def current_token(self):
    if self.index >= self._tokens_len:
      return None
    return self._tokens[self.index]

  def process_whitespace(self):
    current_token = self.current_token()
    if current_token.token_type == 'SPACE':
      whitespace_tokens = []
      whitespace_node = Node('SPACES')
      whitespace_node.leaf = True
      self.current_node.members.append(whitespace_node)
      while current_token and current_token.token_type == 'SPACE':
        whitespace_node.members.append(current_token.content)
        self.index += 1
        current_token = self.current_token()

  def build_parse_tree(self):
    if not self.current_node:
      top_node = Node('MODULE')
      self.current_node = top_node
    if not self._tokens or self._tokens_len == 0:
      return None
    # Consume any leading whitespace.
    self.process_whitespace()
    return top_node
    


def parse_tokens(tokens):
  parser = Parser(tokens)
  return parser.build_parse_tree()


def parse_source(source_code):
  return parse_tokens(lexer.tokenize(source_code))

