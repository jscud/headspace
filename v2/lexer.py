
# Token types checklist:
# identifier - done
# number literal - done
# string literal - done
#    single or double quotes - done
# comments
#    multi-line done
#    single-line done
# symbol - done
# space - done

class Token:
  def __init__(self, content, token_type):
    self.content = content
    self.token_type = token_type

  def print(self, indent_level=0):
    if self.token_type == 'SPACE':
      print(' ' * indent_level, self.token_type, '[', self.content, ']')
    else:
      print(' ' * indent_level, self.token_type, self.content)

  def matches(self, target_type, target_content):
    return self.token_type == target_type and self.content == target_content


class Tokenizer:

  def __init__(self, source_code):
    self._source_code = source_code
    self._source_len = len(source_code)
    self.buffer = []
    self.index = 0

  def current_char(self):
    if self.index < self._source_len:
      return self._source_code[self.index]
    return None

  def next_char(self):
    if self.index < self._source_len - 1:
      return self._source_code[self.index + 1]
    return None

  def prev_char(self):
    if self.index > 0:
      return self._source_code[self.index - 1]
    return None

  def next_identifier(self):
    self.buffer.append(self.current_char())
    next_char = self.next_char()
    while next_char is not None and (next_char.isalnum() or next_char == '_'):
      self.index += 1
      self.buffer.append(self.current_char())
      next_char = self.next_char()
    self.index += 1
    contents = ''.join(self.buffer)
    self.buffer = []
    return Token(contents, 'IDENTIFIER')
    
  def next_number(self):
    self.buffer.append(self.current_char())
    next_char = self.next_char()
    has_encountered_dot = False
    while next_char is not None and (next_char.isnumeric() or (next_char == '.' and not has_encountered_dot)):
      self.index += 1
      self.buffer.append(self.current_char())
      if self.current_char() == '.':
        has_encountered_dot = True
      next_char = self.next_char()
    self.index += 1
    contents = ''.join(self.buffer)
    self.buffer = []
    return Token(contents, 'NUMBER')
    
  def next_space(self):
    self.buffer.append(self.current_char())
    next_char = self.next_char()
    while next_char is not None and next_char.isspace():
      self.index += 1
      self.buffer.append(self.current_char())
      next_char = self.next_char()
    self.index += 1
    contents = ''.join(self.buffer)
    self.buffer = []
    return Token(contents, 'SPACE')

  def next_string(self):
    self.buffer.append(self.current_char())
    next_char = self.next_char()
    quote_char = self.current_char()
    escaped_mode = False
    while next_char is not None and (next_char != quote_char or escaped_mode):
      self.index += 1
      self.buffer.append(self.current_char())
      if escaped_mode:
        escaped_mode = False
      elif self.current_char() == '\\':
        escaped_mode = True
      next_char = self.next_char()
    self.index += 1
    if self.current_char() == quote_char:
      self.buffer.append(self.current_char())
      self.index += 1
    contents = ''.join(self.buffer)
    self.buffer = []
    return Token(contents, 'STRING')
    
  def next_comment(self):
    # Adds the opening /
    self.buffer.append(self.current_char())
    next_char = self.next_char()
    # Now add the next part of the opening, the * or /
    self.buffer.append(next_char)
    single_line_comment = next_char == '/'
    self.index += 1
    next_char = self.next_char()
    if single_line_comment: # This part is broken.
      while next_char is not None and next_char != '\n' and next_char != '\r':
        self.index += 1
        self.buffer.append(self.current_char())
        next_char = self.next_char()
      if next_char == '\n' or next_char == '\r':
        self.index += 1
        # Append the closing newline as part of the comment.
        self.buffer.append(self.current_char())
        self.index += 1
    else:
      about_to_close = False
      while next_char is not None:
        self.index += 1
        if self.current_char() == '*' and about_to_close == False:
          about_to_close = True
        self.buffer.append(self.current_char())
        next_char = self.next_char()
        if about_to_close and next_char == '/':
          self.index += 1
          self.buffer.append(self.current_char())
          self.index += 1
          break
        elif about_to_close:
          about_to_close = False
    contents = ''.join(self.buffer)
    self.buffer = []
    return Token(contents, 'COMMENT')
    
  def next_symbol(self):
    # Always a single character.
    contents = self.current_char()
    self.index += 1
    return Token(contents, 'SYMBOL')

  def next_token(self):
    if self.current_char() is None:
      return None
    elif self.current_char().isalpha():
      return self.next_identifier()
    elif self.current_char().isnumeric():
      return self.next_number()
    elif self.current_char().isspace():
      return self.next_space()
    elif self.current_char() == '\'' or self.current_char() == '"':
      return self.next_string()
    elif self.current_char() == '/' and (self.next_char() == '*' or self.next_char() == '/'):
      return self.next_comment()
    else:
      return self.next_symbol()


def tokenize(source_code):
  tokenizer = Tokenizer(source_code)
  tokens = []
  current_token = tokenizer.next_token()
  while current_token is not None:
    tokens.append(current_token)
    current_token = tokenizer.next_token()
  return tokens

