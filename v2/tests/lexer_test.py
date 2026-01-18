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


if __name__ == '__main__':
  unittest.main()

