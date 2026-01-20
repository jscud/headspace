import unittest
import parser


HELLO_WORLD_EXAMPLE = """
    main: function[][
      os.print["Hello World\\n"]
    ]
"""


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

  def test_parses_variable_declaration(self):
    tree = parser.parse_source('x: int32')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('DECLARATION', tree.members[0].node_type)
    self.assertEqual('IDENTIFIER', tree.members[0].members[0].node_type)
    self.assertEqual('x', tree.members[0].members[0].members[0])
    self.assertEqual('SYMBOL', tree.members[0].members[1].node_type)
    self.assertEqual(':', tree.members[0].members[1].members[0])
    self.assertEqual('SPACES', tree.members[0].members[2].node_type)
    self.assertEqual('VARIABLE_TYPE', tree.members[0].members[3].node_type)
    self.assertEqual('int32', tree.members[0].members[3].members[0])
    
  def todo_test_parse_hello_world_example(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    print('Parsing sample program')
    print(HELLO_WORLD_EXAMPLE)
    self.assertEqual('MODULE', tree.node_type)
    tree.print()
    


if __name__ == '__main__':
  unittest.main()

