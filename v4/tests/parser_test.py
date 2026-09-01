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

PARAMS_EXAMPLE = """
function addNumbers type.int32 (param a type.int32, param b type.int32) {
  return math.addInts(a, b)
}

function main type.void () {
  os.printInt(addNumbers(10, 9))
}
"""

CLASS_EXAMPLE = """
class ExampleClass {
  member name type.str
  member age type.int32

  constructor (param name type.str, param age type.int32) {
    set this.name = name
    set this.age = age
  }

  method sayIntro type.void () {
    os.print("Name: ")
    os.print(this.name)
    os.print("\\nAge: ")
    os.printInt(this.age)
    os.print("\\n")
  }
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

  def test_parses_function_params(self):
    tree = parser.parse_source(PARAMS_EXAMPLE)
    self.assertTreeContains("""
      FUNCTION_DECLARATION:
        FUNCTION_NAME:
          addNumbers
        TYPE_CHAIN:
          INITIAL_TYPE:
            int32
        PARAMETER_DECLARATIONS:
          PARAMETER:
            PARAMETER_NAME:
              a
            TYPE_CHAIN:
              INITIAL_TYPE:
                int32
          PARAMETER:
            PARAMETER_NAME:
              b
            TYPE_CHAIN:
              INITIAL_TYPE:
                int32
        CODE_BLOCK:
          RETURN_STATEMENT:
            FUNCTION_CALL:
              ACCESS_CHAIN:
                INITIAL_IDENTIFIER:
                  math
                CHAINED_IDENTIFIER:
                  addInts
              ARGUMENTS_LIST:
                ACCESS_CHAIN:
                  INITIAL_IDENTIFIER:
                    a
                ACCESS_CHAIN:
                  INITIAL_IDENTIFIER:
                    b""", tree)
    self.assertTreeContains("""
      FUNCTION_CALL:
        ACCESS_CHAIN:
          INITIAL_IDENTIFIER:
            os
          CHAINED_IDENTIFIER:
            printInt
        ARGUMENTS_LIST:
          FUNCTION_CALL:
            ACCESS_CHAIN:
              INITIAL_IDENTIFIER:
                addNumbers
            ARGUMENTS_LIST:
              NUMBER_LITERAL:
                10
              NUMBER_LITERAL:
                9""", tree)

  def test_parses_class_definition(self):
    tree = parser.parse_source(CLASS_EXAMPLE)
    self.assertTreeContains("""
      CLASS_DECLARATION:
        CLASS_NAME:
          ExampleClass
        CODE_BLOCK:
          MEMBER_DECLARATION:
            MEMBER_NAME:
              name
            TYPE_CHAIN:
              INITIAL_TYPE:
                str
          MEMBER_DECLARATION:
            MEMBER_NAME:
              age
            TYPE_CHAIN:
              INITIAL_TYPE:
                int32
          CONSTRUCTOR_DEFINITION:
            PARAMETER_DECLARATIONS:
              PARAMETER:
                PARAMETER_NAME:
                  name
                TYPE_CHAIN:
                  INITIAL_TYPE:
                    str
              PARAMETER:
                PARAMETER_NAME:
                  age
                TYPE_CHAIN:
                  INITIAL_TYPE:
                    int32
            CODE_BLOCK:
              ASSIGNMENT_STATEMENT:
                ASSIGNMENT_TARGET:
                  ACCESS_CHAIN:
                    INITIAL_IDENTIFIER:
                      this
                    CHAINED_IDENTIFIER:
                      name
                ASSIGNMENT_TARGET:
                  ACCESS_CHAIN:
                    INITIAL_IDENTIFIER:
                      name
              ASSIGNMENT_STATEMENT:
                ASSIGNMENT_TARGET:
                  ACCESS_CHAIN:
                    INITIAL_IDENTIFIER:
                      this
                    CHAINED_IDENTIFIER:
                      age
                ASSIGNMENT_TARGET:
                  ACCESS_CHAIN:
                    INITIAL_IDENTIFIER:
                      age
          METHOD_DECLARATION:
            METHOD_NAME:
              sayIntro
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
                    print""", tree)


if __name__ == '__main__':
  unittest.main()
