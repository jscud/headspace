
import sys

import lexer


# Parse tree checklist:
# function call - done
# nested function call - done
# function declaration - done
# foreign code block - done
# variable declaration - done
# conditional statement (if) - done
# loop statement (while) - done
# assigment statement - done
# module name - done
# return statement - done
# infix operators - done
# postfix operators - done
# pass through comments
# class declaration - done
# importing modules - done
# allocation memory
# passing references


INFIX_OPERATORS = ['+', '==', '-', '<', '>']
POSTFIX_OPERATORS = ['++', '--']


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


class Parser:

  def __init__(self, tokens):
    self._tokens = tokens
    self._tokens_len = len(tokens)
    self.index = 0
    self.debug_print = False
    self.debug_indent = 0

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
        print(' ' * self.debug_indent, end='')
        print('consumed@', debug_note)
        print(' ' * (self.debug_indent + 2), end='')
        self.current_token().print()
    self.index += 1

  def enter_method(self, debug_note):
    if self.debug_print:
      print(' ' * self.debug_indent, end='')
      print('/ entering ', debug_note)
      self.debug_indent += 4

  def leave_method(self, debug_note):
    if self.debug_print:
      self.debug_indent -= 4
      if self.debug_indent < 0:
        print('error, enter and leave mismatch')
        sys.exit(1)
      print(' ' * self.debug_indent, end='')
      print('\\  leaving ', debug_note)

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
    self.enter_method('process_identifier_chain')
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
    self.leave_method('process_identifier_chain')

  def process_argument_list(self, parent_node):
    self.enter_method('process_argument_list')
    current_token = self.current_token()
    argument_list = Node('ARGUMENTS')
    while current_token and not current_token.matches('SYMBOL', ']'):
      next_token = self.next_token()
      if next_token and next_token.token_type == 'SYMBOL' and next_token.content in INFIX_OPERATORS:
        self.process_infix_operation(argument_list)
      elif current_token.matches('SYMBOL', ','):
        self.consume_current_token('processed argument seperator in arguments list')
      elif current_token.token_type == 'STRING':
        argument_list.members.append(Node('STRING_LITERAL', [current_token.content], True))
        self.consume_current_token('processed string literal argument')
      elif current_token.token_type == 'NUMBER':
        argument_list.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
        self.consume_current_token('processed number literal argument')
      elif current_token.token_type == 'IDENTIFIER':
        # This may be an identifier chain or a function call. We can process it as an rvalue.
        self.process_rvalue(argument_list)
      self.process_whitespace(argument_list)
      current_token = self.current_token()
    parent_node.members.append(argument_list)
    self.leave_method('process_argument_list')

  def process_function_call(self, parent_node):
    # Starts with an identifier followed by [.
    self.enter_method('process_function_call')
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
    self.leave_method('process_function_call')

  def process_foreign_code_block(self, parent_node):
    self.enter_method('process_foreign_code_block')
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
    self.leave_method('process_foreign_code_block')

  def process_infix_operation(self, parent_node):
    self.enter_method('process_infix_operation')
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
      self.consume_current_token('processed second string operand in infix')
    elif current_token and current_token.token_type == 'NUMBER':
      # Move past the first operand.
      infix_operation.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
      self.consume_current_token('processed second number operand in infix')
    elif current_token and current_token.token_type == 'IDENTIFIER':
      self.process_identifier_chain(infix_operation)
    parent_node.members.append(infix_operation)
    self.leave_method('process_infix_operation')

  def process_class_instantiation(self, parent_node):
    self.enter_method('process_class_instantiation')
    class_instantiation = Node('CLASS_INSTANTIATION')
    current_token = self.current_token()
    if not current_token or not current_token.matches('IDENTIFIER', 'new'):
      print('Class instantiation must begin with new keyword')
      sys.exit(1)
    class_instantiation.members.append(Node('NEW_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed new keyowrd in class instantiation')
    # The new keyword should be followed by what looks like a function call, executing the constructor.
    self.process_whitespace(class_instantiation)
    self.process_identifier_chain(class_instantiation)
    self.process_whitespace(class_instantiation)
    self.process_function_call(class_instantiation)
    parent_node.members.append(class_instantiation)
    self.leave_method('process_class_instantiation')

  def process_delete_statment(self, parent_node):
    self.enter_method('process_delete_statment')
    delete_statement = Node('DELETE_STATEMENT')
    current_token = self.current_token()
    if not current_token or not current_token.matches('IDENTIFIER', 'delete'):
      print('Delete statement must begin with delete keyword')
      sys.exit(1)
    delete_statement.members.append(Node('DELETE_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed delete keyowrd in delete statement')
    # The delete keyword should be followed by an identifier.
    self.process_whitespace(delete_statement)
    self.process_identifier_chain(delete_statement)
    self.process_whitespace(delete_statement)
    parent_node.members.append(delete_statement)
    self.leave_method('process_delete_statment')

  def process_rvalue(self, parent_node):
    self.enter_method('process_rvalue')
    current_token = self.current_token()
    # Lookahead to see if there is a symbol for an infix operation.
    next_token = self.next_token()
    if next_token and next_token.token_type == 'SYMBOL' and next_token.content in INFIX_OPERATORS:
      self.process_infix_operation(parent_node)
      self.process_whitespace(parent_node)
    elif next_token and next_token.token_type == 'SYMBOL' and next_token.content in POSTFIX_OPERATORS:
      self.process_postfix_operation(parent_node)
      self.process_whitespace(parent_node)
    elif current_token and current_token.token_type == 'STRING':
      parent_node.members.append(Node('STRING_LITERAL', [current_token.content], True))
      self.consume_current_token('processed string rvalue')
    elif current_token and current_token.token_type == 'NUMBER':
      parent_node.members.append(Node('NUMBER_LITERAL', [current_token.content], True))
      self.consume_current_token('processed number rvalue')
    elif current_token and current_token.token_type == 'IDENTIFIER':
      if current_token.content == 'new':
        self.process_class_instantiation(parent_node)
      else:
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
    self.leave_method('process_rvalue')

  def process_postfix_operation(self, parent_node):
    self.enter_method('process_postfix_operation')
    postfix_operation = Node('POSTFIX_OPERATION')
    current_token = self.current_token()
    if current_token and current_token.token_type == 'IDENTIFIER':
      self.process_identifier_chain(postfix_operation)
    self.process_whitespace(postfix_operation)
    current_token = self.current_token()
    if current_token and current_token.token_type != 'SYMBOL':
      print('In an postfix operation, the symbol should follow the identifier.')
      sys.exit(1)
    if current_token and current_token.token_type == 'SYMBOL' and current_token.content in POSTFIX_OPERATORS:
      postfix_operation.members.append(Node('OPERATOR', [current_token.content], True))
    # Move past the operator.
    self.consume_current_token('processed postfix operator')
    self.process_whitespace(postfix_operation)
    parent_node.members.append(postfix_operation)
    self.leave_method('process_postfix_operation')

  def process_assignment_statement(self, parent_node):
    self.enter_method('process_assignment_statement')
    current_token = self.current_token()
    assignment = Node('ASSIGNMENT')
    if not current_token or not current_token.matches('SYMBOL', '='):
      print('Expected assignment to have a = after the identifier')
      sys.exit(1)
    assignment.members.append(Node('ASSIGNMENT_SYMBOL', [current_token.content], True))
    self.consume_current_token('processed assignment symbol')
    self.process_whitespace(assignment)
    self.process_rvalue(assignment)
    parent_node.members.append(assignment)
    self.leave_method('process_assignment_statement')

  def process_assignment(self, parent_node):
    self.enter_method('process_assignment')
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
    self.leave_method('process_assignment')

  def process_return_statement(self, parent_node):
    self.enter_method('process_return_statement')
    current_token = self.current_token()
    return_statement = Node('RETURN_STATEMENT')
    if not current_token or not current_token.matches('IDENTIFIER', 'return'):
      print('Expected a return statement to start with return')
      sys.exit(1)
    self.consume_current_token('processed return identifier')
    self.process_whitespace(return_statement)
    self.process_rvalue(return_statement)
    parent_node.members.append(return_statement)
    self.leave_method('process_return_statement')

  def process_condition_expression(self, parent_node):
    self.enter_method('process_condition_expression')
    current_token = self.current_token()
    condition_expression = Node('CONDITION_EXPRESSION')
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('condition expression must start with an opening [')
      sys.exit(1)
    condition_expression.members.append(Node('CONDITION_EXPRESSION_START', [current_token.content], True))
    self.consume_current_token('processed opening [ in condition expresion')
    self.process_whitespace(condition_expression)
    current_token = self.current_token()
    self.process_rvalue(condition_expression)
    self.process_whitespace(condition_expression)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', ']'):
      print('condition expression must end with an closing ]')
      sys.exit(1)
    condition_expression.members.append(Node('CONDITION_EXPRESSION_END', [current_token.content], True))
    self.consume_current_token('processed closing ] in condition expresion')
    parent_node.members.append(condition_expression)
    self.leave_method('process_condition_expression')

  def process_if_statement(self, parent_node):
    self.enter_method('process_if_statement')
    current_token = self.current_token()
    if_statement = Node('IF_STATEMENT')
    if not current_token or not current_token.matches('IDENTIFIER', 'if'):
      print('Expected an if statement to start with if')
      sys.exit(1)
    if_statement.members.append(Node('IF_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed if identifier')
    self.process_whitespace(if_statement)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('The if keyword must be followed by an opening [')
      sys.exit(1)
    # Conditions
    self.process_condition_expression(if_statement)
    self.process_whitespace(if_statement)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('The if expression must be followed by a code block')
      sys.exit(1)
    #TODO: Need to decide if the inner code blocks inside of a function should
    # perhaps be more restricted by not allowing variable declarations.
    self.process_code_block(if_statement)
    self.process_whitespace(if_statement)
    current_token = self.current_token()
    # Check to see if this if statement includes an else clause.
    if current_token and current_token.matches('IDENTIFIER', 'else'):
      if_statement.members.append(Node('ELSE_KEYWORD', [current_token.content], True))
      self.consume_current_token('processed else identifier')
      self.process_whitespace(if_statement)
      current_token = self.current_token()
      if not current_token or not current_token.matches('SYMBOL', '['):
        print('The else expression must be followed by a code block')
        sys.exit(1)
      self.process_code_block(if_statement)
      self.process_whitespace(if_statement)
    parent_node.members.append(if_statement)
    self.leave_method('process_if_statement')

  def process_while_statement(self, parent_node):
    self.enter_method('process_while_statement')
    current_token = self.current_token()
    while_statement = Node('WHILE_STATEMENT')
    if not current_token or not current_token.matches('IDENTIFIER', 'while'):
      print('Expected a while statement to start with while')
      sys.exit(1)
    while_statement.members.append(Node('WHILE_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed while identifier')
    self.process_whitespace(while_statement)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('The while keyword must be followed by an opening [')
      sys.exit(1)
    # Conditions
    self.process_condition_expression(while_statement)
    self.process_whitespace(while_statement)
    current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('The while expression must be followed by a code block')
      sys.exit(1)
    #TODO: Need to decide if the inner code blocks inside of a function should
    # perhaps be more restricted by not allowing variable declarations.
    self.process_code_block(while_statement)
    self.process_whitespace(while_statement)
    current_token = self.current_token()
    parent_node.members.append(while_statement)
    self.leave_method('process_while_statement')

  def process_code_block(self, parent_node):
    self.enter_method('process_code_block')
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
      next_token = self.next_token()
      if current_token.content.startswith('BEGIN_FOREIGN_CODE_'):
        self.process_foreign_code_block(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif current_token.content == 'return':
        self.process_return_statement(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif current_token.content == 'if':
        self.process_if_statement(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif current_token.content == 'while':
        self.process_while_statement(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif current_token.content == 'delete':
        self.process_delete_statment(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif next_token and next_token.matches('SYMBOL', ':'):
        declaration_tree = Node('DECLARATION')
        declaration_tree.members.append(Node('IDENTIFIER', [current_token.content], True))
        self.consume_current_token('processed declared identifier in code block')
        self.process_whitespace(declaration_tree)
        current_token = self.current_token()
        if current_token and current_token.matches('SYMBOL', ':'):
          declaration_tree.members.append(Node('DECLARATION_MARKER', [':'], True))
        else:
          print('Expected : following variable identifer was missing from declaration')
          sys.exit(1)
        self.consume_current_token('processed declaration marker in code block')
        current_token = self.current_token()
        if current_token and current_token.matches('IDENTIFIER', 'function'):
          print('A function cannot be declared in a code block')
          sys.exit(1)
        if not current_token or not current_token.token_type == 'IDENTIFIER':
          print('Variable declaration must end with a type for the variable')
          sys.exit(1)
        else:
          declaration_tree.members.append(Node('VARIABLE_TYPE', [current_token.content], True))
          self.consume_current_token('processed type identifier in variable declaration')
          code_block.members.append(declaration_tree)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif next_token and next_token.matches('SYMBOL', '='):
        # This is assigning a variable a value.
        self.process_assignment(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif next_token and next_token.content in INFIX_OPERATORS:
        self.process_infix_operation(code_block)
        self.process_whitespace(code_block)
        current_token = self.current_token()
      elif next_token and next_token.content in POSTFIX_OPERATORS:
        self.process_postfix_operation(code_block)
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
        elif current_token and current_token.matches('SYMBOL', '='):
          self.process_assignment_statement(sub_node)
          sub_node.node_type = 'MEMBER_ASSIGNMENT'
          code_block.members.append(sub_node)
        self.process_whitespace(sub_node)
        current_token = self.current_token()
    self.process_whitespace(code_block)
    current_token = self.current_token()
    if current_token and current_token.matches('SYMBOL', ']'):
      code_block.members.append(Node('CODE_BLOCK_END', [current_token.content], True))
    self.consume_current_token('processed the closing ] for a code block')
    parent_node.members.append(code_block)
    self.leave_method('process_code_block')

  def process_parameters_list(self, parent_node):
    self.enter_method('process_parameters_list')
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
      self.process_whitespace(declaration_tree)
      parent_node.members.append(declaration_tree)
      current_token = self.current_token()
    self.leave_method('process_parameters_list')

  def process_function_definition(self, parent_node):
    self.enter_method('process_function_definition')
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
    if not current_token or not current_token.matches('SYMBOL', ':'):
      print('Expected a : to express the return type in function definition')
      sys.exit(1)
    self.consume_current_token('processed return type separator in function declaration')
    self.process_whitespace(function_definition)
    current_token = self.current_token()
    # After the function keyword, we expect the return type.
    if not current_token or not current_token.token_type == 'IDENTIFIER':
      print('Expected a return type for the function after the function keyword in function definition')
      sys.exit(1)
    function_definition.members.append(Node('FUNCTION_RETURN_TYPE', [current_token.content], True))
    self.consume_current_token('processed function return type in function declaration')
    self.process_whitespace(function_definition)
    current_token = self.current_token()
    # Should be an opening [ for the parameter list.
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a [ after the function\'s return type in function definition')
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
    parent_node.members.append(function_definition)
    self.leave_method('process_function_definition')

  def process_class_definition(self, parent_node):
    self.enter_method('process_class_definition')
    current_token = self.current_token()
    # The current token is the identifier 'class' to begin the declaration.
    class_definition = Node('CLASS_DEFINITION')
    if not current_token or not current_token.matches('IDENTIFIER', 'class'):
      print('class definition did not begin with keyword class')
      sys.exit(1)
    class_definition.members.append(Node('CLASS_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed class keyword in class declaration')
    self.process_whitespace(class_definition)
    current_token = self.current_token()
    # TODO: Support class inheritance by allowing a : parent_type pattern after the class keyword.
    # Should be an opening [ for the list of members and methods.
    if not current_token or not current_token.matches('SYMBOL', '['):
      print('Expected a [ after the class name in class definition')
      sys.exit(1)
    class_definition.members.append(Node('CLASS_MEMBERS_START', [current_token.content], True))
    self.consume_current_token('processed opening [ in class members declaration')
    self.process_whitespace(class_definition)
    current_token = self.current_token()
    while current_token and current_token.token_type == 'IDENTIFIER':
      self.process_declaration(class_definition)
      self.process_whitespace(class_definition)
      current_token = self.current_token()
    if not current_token or not current_token.matches('SYMBOL', ']'):
      print('Expected a ] after the first [ in a class definition')
      sys.exit(1)
    class_definition.members.append(Node('CLASS_MEMBERS_END', [current_token.content], True))
    self.consume_current_token('processed closing ] in class members declaration')
    self.process_whitespace(class_definition)
    parent_node.members.append(class_definition)
    self.leave_method('process_class_definition')

  def process_declaration(self, parent_node):
    self.enter_method('process_declaration')
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
    elif current_token and current_token.matches('IDENTIFIER', 'class'):
      # This is a class declaration.
      declaration_tree.node_type = 'CLASS_DECLARATION'
      self.process_class_definition(declaration_tree)
    else:
      # This is a variable declaration, use this identifier as the type.
      declaration_tree.members.append(Node('VARIABLE_TYPE', [current_token.content], True))
      self.consume_current_token('processed variable type identifier in declaration')
    parent_node.members.append(declaration_tree)
    self.leave_method('process_declaration')

  def process_import_statement(self, parent_node):
    self.enter_method('process_import')
    current_token = self.current_token()
    import_tree = Node('IMPORT_STATEMENT')
    if not current_token or not current_token.matches('IDENTIFIER', 'import'):
      print('Import statements must start with keyword import')
      sys.exit(1)
    import_tree.members.append(Node('IMPORT_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed import keyword')
    self.process_whitespace(import_tree)
    current_token = self.current_token()
    if not current_token or current_token.token_type != 'STRING':
      print('The import keyword must be followed by a string with the path of the module.')
      sys.exit(1)
    import_tree.members.append(Node('MODULE_LOCATION', [current_token.content], True))
    self.consume_current_token('processed import module location')
    self.process_whitespace(import_tree)
    current_token = self.current_token()
    if not current_token or not current_token.matches('IDENTIFIER', 'as'):
      print('The import statement must include as moduleName in the form import "module_id" as moduleName.')
      sys.exit(1)
    import_tree.members.append(Node('AS_KEYWORD', [current_token.content], True))
    self.consume_current_token('processed the \'as\' keyword in import statement')
    self.process_whitespace(import_tree)
    current_token = self.current_token()
    if not current_token or not current_token.token_type == 'IDENTIFIER':
      print('The import must end with the module name\'s identifier.')
      sys.exit(1)
    import_tree.members.append(Node('MODULE_NAME', [current_token.content], True))
    self.consume_current_token('processed module name in import statement')
    self.process_whitespace(import_tree)
    parent_node.members.append(import_tree)
    self.leave_method('process_import')

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
        elif next_token.content in INFIX_OPERATORS:
          self.process_infix_operation(top_node)
        elif next_token.content in POSTFIX_OPERATORS:
          self.process_postfix_operation(top_node)
      elif current_token.content == 'import':
        self.process_import_statement(top_node)
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

