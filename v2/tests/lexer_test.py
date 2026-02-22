import unittest
import lexer


class TestLexerTokenize(unittest.TestCase):
  """Exercises the tokenizer."""

  def assertTokens(self, sequence, tokens):
    index = 0
    self.assertEqual(len(sequence), len(tokens))
    for token in tokens:
      self.assertEqual(sequence[index][0], tokens[index].token_type)
      self.assertEqual(sequence[index][1], tokens[index].content)
      index += 1

  def test_first_example(self):
    """Simple example program."""
    tokens = lexer.tokenize('simple example')
    self.assertEqual(3, len(tokens))
    self.assertEqual('simple', tokens[0].content)
    self.assertEqual('IDENTIFIER', tokens[0].token_type)
    self.assertEqual(' ', tokens[1].content)
    self.assertEqual('SPACE', tokens[1].token_type)
    self.assertEqual('example', tokens[2].content)
    self.assertEqual('IDENTIFIER', tokens[2].token_type)
    self.assertTokens((
          ('IDENTIFIER', 'simple'),
          ('SPACE', ' '),
          ('IDENTIFIER', 'example')
        ), tokens)

  def test_tokenizer_identifiers_and_whitespace(self):
    sample_code = 'x y     multi_with_underscore   camelCase\nx1\ta2 \nc'
    tokens = lexer.tokenize(sample_code)
    self.assertTokens((
          ('IDENTIFIER', 'x'),
          ('SPACE', ' '),
          ('IDENTIFIER', 'y'),
          ('SPACE', '     '),
          ('IDENTIFIER', 'multi_with_underscore'),
          ('SPACE', '   '),
          ('IDENTIFIER', 'camelCase'),
          ('SPACE', '\n'),
          ('IDENTIFIER', 'x1'),
          ('SPACE', '\t'),
          ('IDENTIFIER', 'a2'),
          ('SPACE', ' \n'),
          ('IDENTIFIER', 'c')
        ), tokens)

  def test_tokenize_numbers(self):
    sample_code = '5 12 98234823 3.14 56.7.8.9'
    tokens = lexer.tokenize(sample_code)
    self.assertTokens((
          ('NUMBER', '5'),
          ('SPACE', ' '),
          ('NUMBER', '12'),
          ('SPACE', ' '),
          ('NUMBER', '98234823'),
          ('SPACE', ' '),
          ('NUMBER', '3.14'),
          ('SPACE', ' '),
          ('NUMBER', '56.7'),
          ('SYMBOL', '.'),
          ('NUMBER', '8.9')
        ), tokens)

  def test_tokenize_strings(self):
    sample_code = '\'hello\',\'it\\\'s inline\' "double quotes"-"it\'s great" \'to "mix"\''
    tokens = lexer.tokenize(sample_code)
    self.assertTokens((
          ('STRING', '\'hello\''),
          ('SYMBOL', ','),
          ('STRING', '\'it\\\'s inline\''),
          ('SPACE', ' '),
          ('STRING', '"double quotes"'),
          ('SYMBOL', '-'),
          ('STRING', '"it\'s great"'),
          ('SPACE', ' '),
          ('STRING', '\'to "mix"\'')
        ), tokens)

  def test_tokenize_comments(self):
    sample_code = '/**/ /* */ /******/ /* * /*/x//\n//*single line\n1'
    tokens = lexer.tokenize(sample_code)
    self.assertTokens((
          ('COMMENT', '/**/'),
          ('SPACE', ' '),
          ('COMMENT', '/* */'),
          ('SPACE', ' '),
          ('COMMENT', '/******/'),
          ('SPACE', ' '),
          ('COMMENT', '/* * /*/'),
          ('IDENTIFIER', 'x'),
          ('COMMENT', '//\n'),
          ('COMMENT', '//*single line\n'),
          ('NUMBER', '1')
        ), tokens)

  def test_tokenize_symbols(self):
    sample_code = 'ab,c/d+e;=$f:g.h'
    tokens = lexer.tokenize(sample_code)
    self.assertTokens((
          ('IDENTIFIER', 'ab'),
          ('SYMBOL', ','),
          ('IDENTIFIER', 'c'),
          ('SYMBOL', '/'),
          ('IDENTIFIER', 'd'),
          ('SYMBOL', '+'),
          ('IDENTIFIER', 'e'),
          ('SYMBOL', ';'),
          ('SYMBOL', '='),
          ('SYMBOL', '$'),
          ('IDENTIFIER', 'f'),
          ('SYMBOL', ':'),
          ('IDENTIFIER', 'g'),
          ('SYMBOL', '.'),
          ('IDENTIFIER', 'h')
        ), tokens)


if __name__ == '__main__':
  unittest.main()

