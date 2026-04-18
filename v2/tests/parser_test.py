import unittest
import parser


HELLO_WORLD_EXAMPLE = """
    main: function: void[][
      os.print["Hello World\\n"]
    ]
"""

FOREIGN_CODE_EXAMPLE = """
main: function: void[][
  BEGIN_FOREIGN_CODE_C
  int x = 10;
  printf("Hello World\\n");
  printf("%i\\n", x);
  END_FOREIGN_CODE_C
]
"""

RETURN_VALUE_EXAMPLE = """
    sixseven: function: int32[][
      return 67
    ]
"""

IF_ELSE_EXAMPLE = """
main:function:void[][
  a:int32
  a = 5
  if[a == 5][
    os.print["Yes, a is 5.\\n"]
  ] else [
    os.print["No, a is not 5.\\n"]
  ]
]
"""

WHILE_EXAMPLE = """
main:function:void[][
  counter:int32
  counter = 0
  while[counter < 5][
    counter++
  ]
]
"""

DATA_CLASS_EXAMPLE = """
DataClass: class [
  x: int
]

main: function: void[][
  instance:DataClass
  instance.x = 42
  os.print["Class member x: "]
  os.printInt[instance.x]
  os.print["\\n"]
]
"""



class TestParserParse(unittest.TestCase):
  """Exercises the parser."""

  def assertTreeContains(self, needle, tree):
    self.assertTrue(needle in tree.dump())

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
    self.assertTreeContains("""
  DECLARATION:
    IDENTIFIER:
      x
    DECLARATION_MARKER:
      :
    VARIABLE_TYPE:
      int32""", tree)

  def test_parse_hello_world_example(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('FUNCTION_DECLARATION', tree.members[0].node_type)
    self.assertEqual('IDENTIFIER', tree.members[0].members[0].node_type)
    self.assertEqual('main', tree.members[0].members[0].members[0])
    self.assertEqual('FUNCTION_DEFINITION', tree.members[0].members[2].node_type)
    self.assertEqual('FUNCTION_KEYWORD', tree.members[0].members[2].members[0].node_type)
    self.assertEqual('function', tree.members[0].members[2].members[0].members[0])
    self.assertEqual('FUNCTION_RETURN_TYPE', tree.members[0].members[2].members[1].node_type)
    self.assertEqual('void', tree.members[0].members[2].members[1].members[0])
    self.assertEqual('FUNCTION_PARAMS_START', tree.members[0].members[2].members[2].node_type)
    self.assertEqual('FUNCTION_PARAMS_END', tree.members[0].members[2].members[3].node_type)
    self.assertEqual('CODE_BLOCK', tree.members[0].members[2].members[4].node_type)

  def test_parse_foreign_code_example(self):
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    self.assertEqual('CODE_BLOCK', tree.members[0].members[2].members[4].node_type)
    self.assertEqual('CODE_BLOCK_START', tree.members[0].members[2].members[4].members[0].node_type)
    self.assertEqual('FOREIGN_CODE_BLOCK', tree.members[0].members[2].members[4].members[1].node_type)
    self.assertEqual('CODE_BLOCK_END', tree.members[0].members[2].members[4].members[2].node_type)

  def test_assignment_statement(self):
    tree = parser.parse_source('example = "string literal"')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('ASSIGNMENT', tree.members[0].node_type)
    self.assertEqual('ASSIGNMENT_TARGET', tree.members[0].members[0].node_type)
    self.assertEqual('ASSIGNMENT_SYMBOL', tree.members[0].members[1].node_type)
    self.assertEqual('STRING_LITERAL', tree.members[0].members[2].node_type)

  def test_return_statement(self):
    tree = parser.parse_source(RETURN_VALUE_EXAMPLE)
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('CODE_BLOCK', tree.members[0].members[2].members[4].node_type)
    self.assertEqual('CODE_BLOCK_START', tree.members[0].members[2].members[4].members[0].node_type)
    self.assertEqual('RETURN_STATEMENT', tree.members[0].members[2].members[4].members[1].node_type)
    self.assertEqual('NUMBER_LITERAL', tree.members[0].members[2].members[4].members[1].members[0].node_type)

  def test_function_call_with_identifier_arg(self):
    tree = parser.parse_source('main:function:void[][func[x]]')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('IDENTIFIER_CHAIN', tree.members[0].members[2].members[4].members[1].members[0].node_type)
    self.assertEqual('func', tree.members[0].members[2].members[4].members[1].members[0].members[0].members[0])
    self.assertEqual('FUNCTION_CALL_ARGUMENTS', tree.members[0].members[2].members[4].members[1].members[1].node_type)
    self.assertEqual('IDENTIFIER', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[0].node_type)
    self.assertEqual('x', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[0].members[0])

  def test_nested_function(self):
    tree = parser.parse_source('main:function:void[][outerFunction[innerFunction[67]]]')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('IDENTIFIER_CHAIN', tree.members[0].members[2].members[4].members[1].members[0].node_type)
    self.assertEqual('outerFunction', tree.members[0].members[2].members[4].members[1].members[0].members[0].members[0])
    self.assertEqual('FUNCTION_CALL_ARGUMENTS', tree.members[0].members[2].members[4].members[1].members[1].node_type)
    self.assertEqual('IDENTIFIER', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[0].members[0].node_type)
    self.assertEqual('innerFunction', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[0].members[0].members[0])
    self.assertEqual('FUNCTION_CALL_ARGUMENTS', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[1].node_type)
    self.assertEqual('ARGUMENTS', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[1].members[1].node_type)
    self.assertEqual('NUMBER_LITERAL', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[1].members[1].members[0].node_type)

  def test_function_call_with_infix_operation_arg(self):
    tree = parser.parse_source('main:function:void[][func[9 + 10]]')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual('IDENTIFIER_CHAIN', tree.members[0].members[2].members[4].members[1].members[0].node_type)
    self.assertEqual('func', tree.members[0].members[2].members[4].members[1].members[0].members[0].members[0])
    self.assertEqual('FUNCTION_CALL_ARGUMENTS', tree.members[0].members[2].members[4].members[1].members[1].node_type)
    self.assertEqual('INFIX_OPERATION', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].node_type)
    self.assertEqual('NUMBER_LITERAL', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[0].node_type)
    self.assertEqual('9', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[0].members[0])
    self.assertEqual('10', tree.members[0].members[2].members[4].members[1].members[1].members[1].members[0].members[2].members[0])

  def test_nested_method_and_function_calls(self):
    tree = parser.parse_source('main:function:void[][os.print[text.intToStr[addNumbers[5, 5], 10]]]')
    self.assertTreeContains("""
        FUNCTION_CALL:
          IDENTIFIER_CHAIN:
            IDENTIFIER:
              os
            MEMBER_DOT_ACCESS:
              .
            IDENTIFIER:
              print
          FUNCTION_CALL_ARGUMENTS:
            ARG_LIST_START:
              [
            ARGUMENTS:
              FUNCTION_CALL:
                IDENTIFIER_CHAIN:
                  IDENTIFIER:
                    text
                  MEMBER_DOT_ACCESS:
                    .
                  IDENTIFIER:
                    intToStr
                FUNCTION_CALL_ARGUMENTS:
                  ARG_LIST_START:
                    [
                  ARGUMENTS:
                    FUNCTION_CALL:
                      IDENTIFIER_CHAIN:
                        IDENTIFIER:
                          addNumbers
                      FUNCTION_CALL_ARGUMENTS:
                        ARG_LIST_START:
                          [
                        ARGUMENTS:
                          NUMBER_LITERAL:
                            5
                          NUMBER_LITERAL:
                            5
                        ARG_LIST_END:
                          ]
                    NUMBER_LITERAL:
                      10""", tree)

  def test_function_declaration_includes_type(self):
    tree = parser.parse_source('main:function:void[][os.print[text.intToStr[addNumbers[5, 5], 10]]]')
    self.assertTreeContains("""
    IDENTIFIER:
      main
    DECLARATION_MARKER:
      :
    FUNCTION_DEFINITION:
      FUNCTION_KEYWORD:
        function
      FUNCTION_RETURN_TYPE:
        void
""", tree)

  def test_function_declaration_with_multiple_parameters(self):
    tree = parser.parse_source('addThreeNumbers:function:int32[first:int32, second:int32, third:int32][return first+second]')
    self.assertTreeContains("""
      FUNCTION_PARAMS_START:
        [
      DECLARATION:
        IDENTIFIER:
          first
        DECLARATION_MARKER:
          :
        VARIABLE_TYPE:
          int32
      DECLARATION:
        IDENTIFIER:
          second
        DECLARATION_MARKER:
          :
        VARIABLE_TYPE:
          int32
      DECLARATION:
        IDENTIFIER:
          third
        DECLARATION_MARKER:
          :
        VARIABLE_TYPE:
          int32
      FUNCTION_PARAMS_END:
        ]""", tree)

  def test_if_else_statement(self):
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    self.assertTreeContains("""
        DECLARATION:
          IDENTIFIER:
            a
          DECLARATION_MARKER:
            :
          VARIABLE_TYPE:
            int32
        ASSIGNMENT:
          ASSIGNMENT_TARGET:
            a
          ASSIGNMENT_SYMBOL:
            =
          NUMBER_LITERAL:
            5
        IF_STATEMENT:
          IF_KEYWORD:
            if
          CONDITION_EXPRESSION:
            CONDITION_EXPRESSION_START:
              [
            INFIX_OPERATION:
              IDENTIFIER_CHAIN:
                IDENTIFIER:
                  a
              OPERATOR:
                ==
              NUMBER_LITERAL:
                5
            CONDITION_EXPRESSION_END:
              ]""", tree)
    self.assertTreeContains("""
          ELSE_KEYWORD:
            else
          CODE_BLOCK:
            CODE_BLOCK_START:
              [""", tree)

  def test_while_statement(self):
    tree = parser.parse_source(WHILE_EXAMPLE)
    self.assertTreeContains("""
        WHILE_STATEMENT:
          WHILE_KEYWORD:
            while
          CONDITION_EXPRESSION:
            CONDITION_EXPRESSION_START:
              [
            INFIX_OPERATION:
              IDENTIFIER_CHAIN:
                IDENTIFIER:
                  counter
              OPERATOR:
                <
              NUMBER_LITERAL:
                5
            CONDITION_EXPRESSION_END:
              ]
          CODE_BLOCK:
            CODE_BLOCK_START:
              [
            POSTFIX_OPERATION:
              IDENTIFIER_CHAIN:
                IDENTIFIER:
                  counter
              OPERATOR:
                ++
            CODE_BLOCK_END:
              ]""", tree)

  def test_function_declaration_with_multiple_parameters(self):
    tree = parser.parse_source('import "example_module" as example')
    self.assertTreeContains("""
  IMPORT_STATEMENT:
    IMPORT_KEYWORD:
      import
    MODULE_LOCATION:
      "example_module"
    AS_KEYWORD:
      as
    MODULE_NAME:
      example""", tree)

  def test_simple_class(self):
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    self.assertTreeContains("""
    CLASS_DEFINITION:
      CLASS_KEYWORD:
        class
      CLASS_MEMBERS_START:
        [
      DECLARATION:
        IDENTIFIER:
          x
        DECLARATION_MARKER:
          :
        VARIABLE_TYPE:
          int
      CLASS_MEMBERS_END:
        ]""", tree)


if __name__ == '__main__':
  unittest.main()

