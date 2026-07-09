import unittest
import parser

FOREIGN_CODE_EXAMPLE = """
BEGIN_FOREIGN_CODE:c
#include"somelib.h"
END_FOREIGN_CODE

function foreign type.void () {
  BEGIN_FOREIGN_CODE:c
  printf("Hello\\n");
  END_FOREIGN_CODE
}
"""

FUNCTION_EXAMPLE = """
function sayHello type.void () {
  print("Hello!")
}

function main type.void() {
  sayHello()
}
"""


class TestParserParse(unittest.TestCase):
  """Exercises the parser."""

  def assertTreeContains(self, needle, tree):
    # Check that each line matches without worrying about indentation.
    needle_lines = needle.split('\n')
    tree_lines = tree.dump().split('\n')
    needle_index = 0
    tree_index = 0
    while needle_index < len(needle_lines) and tree_index < len(tree_lines):
      needle_line = needle_lines[needle_index].strip()
      tree_line = tree_lines[tree_index].strip()
      if needle_line == '':
        needle_index += 1
      elif tree_line == needle_line:
        tree_index += 1
        needle_index += 1
      else:
        tree_index += 1
    if needle_index < len(needle_lines):
      print('We never found this expected line:', needle_lines[needle_index])
      self.assertTrue(False)
    else:
      self.assertTrue(True)

  def test_parses_empty_program(self):
    """Empty input, zero length program"""
    tree = parser.parse_source('')
    self.assertIsNone(tree)

  def test_parses_spaces(self):
    tree = parser.parse_source('   \n   ')
    self.assertEqual('MODULE', tree.node_type)
    self.assertEqual(0, len(tree.members))

  def test_parses_module_id(self):
    tree = parser.parse_source('module "my_module_id"')
    self.assertTreeContains("""
      MODULE:
        MODULE_ID:
          "my_module_id" """, tree)

  def test_parses_simple_function(self):
    tree = parser.parse_source('function simple type.void () {os.print("hello\\n")}')
    self.assertTreeContains("""
      FUNCTION_DECLARATION:
        FUNCTION_NAME:
          simple
        TYPE_CHAIN:
          INITIAL_TYPE:
            void
        PARAMETER_DECLARATIONS:
        CODE_BLOCK:
          FUNCTION_CALL:
            ACCESS_CHAIN:
              INITIAL_IDENTIFIER:
                os
              CHAINED_IDENTIFIER:
                print
            ARGUMENTS_LIST:
              STRING_LITERAL:
                "hello\\n" """, tree)

  def test_parses_foreign_code(self):
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    self.assertTreeContains("""
      FOREIGN_CODE:
        TARGET_LANGUAGE:
          c
        TOKENS:""", tree)
    self.assertTreeContains("""
      FOREIGN_TOKEN:
        #
      FOREIGN_TOKEN:
        include
      FOREIGN_TOKEN:
        "somelib.h"
      FOREIGN_TOKEN:""", tree)
    self.assertTreeContains("""
          FOREIGN_TOKEN:
            printf
          FOREIGN_TOKEN:
            (
          FOREIGN_TOKEN:
            "Hello\\n"
          FOREIGN_TOKEN:
            )
          FOREIGN_TOKEN:
            ;""", tree)

  def test_parses_foreign_code(self):
    tree = parser.parse_source(FUNCTION_EXAMPLE)
    self.assertTreeContains("""
      FUNCTION_DECLARATION:
        FUNCTION_NAME:
          sayHello
        TYPE_CHAIN:
          INITIAL_TYPE:
            void
        PARAMETER_DECLARATIONS:
        CODE_BLOCK:
          FUNCTION_CALL:
            ACCESS_CHAIN:
              INITIAL_IDENTIFIER:
                print
            ARGUMENTS_LIST:
              STRING_LITERAL:
                "Hello!"
      FUNCTION_DECLARATION:
        FUNCTION_NAME:
          main
        TYPE_CHAIN:
          INITIAL_TYPE:
            void
        PARAMETER_DECLARATIONS:
        CODE_BLOCK:
          FUNCTION_CALL:
            ACCESS_CHAIN:
              INITIAL_IDENTIFIER:
                sayHello
            ARGUMENTS_LIST:""", tree)


if __name__ == '__main__':
  unittest.main()
