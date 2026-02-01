import unittest
import parser


HELLO_WORLD_EXAMPLE = """
    main: function[][
      os.print["Hello World\\n"]
    ]
"""

FOREIGN_CODE_EXAMPLE = """
main: function[][
  BEGIN_FOREIGN_CODE_C
  int x = 10;
  printf("Hello World\\n");
  printf("%i\\n", x);
  END_FOREIGN_CODE_C
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
    self.assertEqual(0, len(tree.members))

  def test_parses_variable_declaration(self):
    tree = parser.parse_source('x: int32')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('DECLARATION', tree.members[0].node_type)
    self.assertEqual('IDENTIFIER', tree.members[0].members[0].node_type)
    self.assertEqual('x', tree.members[0].members[0].members[0])
    self.assertEqual('DECLARATION_MARKER', tree.members[0].members[1].node_type)
    self.assertEqual(':', tree.members[0].members[1].members[0])
    self.assertEqual('VARIABLE_TYPE', tree.members[0].members[2].node_type)
    self.assertEqual('int32', tree.members[0].members[2].members[0])
    
  def test_parse_hello_world_example(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    #tree.print()
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('FUNCTION_DECLARATION', tree.members[0].node_type)
    self.assertEqual('IDENTIFIER', tree.members[0].members[0].node_type)
    self.assertEqual('main', tree.members[0].members[0].members[0])
    self.assertEqual('FUNCTION_DEFINITION', tree.members[0].members[2].node_type)
    self.assertEqual('FUNCTION_KEYWORD', tree.members[0].members[2].members[0].node_type)
    self.assertEqual('function', tree.members[0].members[2].members[0].members[0])
    self.assertEqual('FUNCTION_PARAMS_START', tree.members[0].members[2].members[1].node_type)
    self.assertEqual('FUNCTION_PARAMS_END', tree.members[0].members[2].members[2].node_type)
    self.assertEqual('CODE_BLOCK', tree.members[0].members[2].members[3].node_type)

  def test_parse_foreign_code_example(self):
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    #tree.print()
    self.assertEqual('CODE_BLOCK', tree.members[0].members[2].members[3].node_type)
    self.assertEqual('CODE_BLOCK_START', tree.members[0].members[2].members[3].members[0].node_type)
    self.assertEqual('FOREIGN_CODE_BLOCK', tree.members[0].members[2].members[3].members[1].node_type)
    self.assertEqual('CODE_BLOCK_END', tree.members[0].members[2].members[3].members[2].node_type)

  def test_assignment_statement(self):
    tree = parser.parse_source('example = "string literal"')
    #tree.print()
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('ASSIGNMENT', tree.members[0].node_type)
    self.assertEqual('ASSIGNMENT_TARGET', tree.members[0].members[0].node_type)
    self.assertEqual('ASSIGNMENT_SYMBOL', tree.members[0].members[1].node_type)
    self.assertEqual('STRING_LITERAL', tree.members[0].members[2].node_type)


if __name__ == '__main__':
  unittest.main()

