import unittest
import parser
import converter
import os

HELLO_WORLD_EXAMPLE = """
module "jeffscudder.com/headspace/tests/hello"

function main type.void () {
  os.print("hello\\n")
}
"""

class TestConverter(unittest.TestCase):
  """Exercises the converter for all languages."""

  def test_symbol_table_for_hello_world(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    local_converter = converter.Converter(tree, 'c')
    local_converter.emit_code()
    self.assertEqual('jeffscudder.com/headspace/tests/hello', local_converter.module_symbol_table.symbols['module'].module_id)
    self.assertEqual(converter.FunctionDef, type(local_converter.module_symbol_table.symbols['main']))
    self.assertEqual('void', local_converter.module_symbol_table.symbols['main'].return_type)

  def test_convert_hello_world_to_c(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    c_converter = converter.Converter(tree, 'c')
    files = c_converter.emit_code()
    self.assertEqual(2, len(files))
    self.assertEqual('headspace/tests/hello.c', files[0].file_path)
    self.assertEqual('headspace/tests/hello.h', files[1].file_path)
    c_content = files[0].content()
    self.assertTrue('#include<stdlib.h>\n' in c_content)
    self.assertTrue('#include<stdint.h>\n' in c_content)
    self.assertTrue('int main(void) {\n' in c_content)
    self.assertTrue('  printf("hello\\n");\n' in c_content)
    self.assertTrue('  return 0;\n' in c_content)
    self.assertTrue('}\n' in c_content)

  def test_convert_hello_world_to_python(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    py_converter = converter.Converter(tree, 'py')
    files = py_converter.emit_code()
    self.assertEqual(1, len(files))
    py_content = files[0].content()
    self.assertTrue('def main():' in py_content)
    self.assertTrue('  print("hello\\n", end="")' in py_content)
    self.assertTrue('if __name__ == "__main__":' in py_content)
    self.assertTrue('  main()' in py_content)

  def test_convert_hello_world_to_go(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    go_converter = converter.Converter(tree, 'go')
    files = go_converter.emit_code()
    go_main_content = files[0].content()
    self.assertTrue('package main' in go_main_content)
    self.assertTrue('import "fmt"' in go_main_content)
    self.assertTrue('func main() {' in go_main_content)
    self.assertTrue('\tfmt.Print("hello\\n")' in go_main_content)

  def test_convert_hello_world_to_javascript(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    js_converter = converter.Converter(tree, 'js')
    files = js_converter.emit_code()
    self.assertEqual(2, len(files))
    js_content = files[0].content()
    self.assertEqual('hello.js', files[0].file_path)
    self.assertEqual('package.json', files[1].file_path)
    self.assertTrue('function main() {' in js_content)
    self.assertTrue('  process.stdout.write("hello\\n");' in js_content)
    self.assertTrue('main();' in js_content)

  def test_convert_hello_world_to_java(self):
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    java_converter = converter.Converter(tree, 'java')
    files = java_converter.emit_code()
    self.assertEqual(1, len(files))
    java_content = files[0].content()
    self.assertEqual(os.path.join('com', 'jeffscudder', 'headspace', 'tests', 'Hello.java'), files[0].file_path)
    self.assertTrue('package com.jeffscudder.headspace.tests;' in java_content)
    self.assertTrue('public class Hello' in java_content)
    self.assertTrue('  public static void main(String[] args) {' in java_content)
    self.assertTrue('    System.out.print("hello\\n");' in java_content)


if __name__ == '__main__':
  unittest.main()

