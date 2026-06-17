import unittest
import parser
import converter

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


if __name__ == '__main__':
  unittest.main()

