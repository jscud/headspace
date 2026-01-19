import unittest
import parser


class TestParserParse(unittest.TestCase):
  """Exercises the parser."""

  def test_parses_empty_program(self):
    """Empty input, zero length program"""
    tree = parser.parse_source('')
    self.assertIsNone(tree)

  def test_parses_spaces(self):
    tree = parser.parse_source('   \n   ')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual(1, len(tree.members))
    self.assertEqual('SPACES', tree.members[0].node_type)


if __name__ == '__main__':
  unittest.main()

