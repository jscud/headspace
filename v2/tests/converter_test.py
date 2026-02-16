import unittest
import parser
import converter
import os
import subprocess


HELLO_WORLD_EXAMPLE = """
moduleName = "hello"

main: function[][
  os.print["Hello World\\n"]
]
"""

class TestConvertToC(unittest.TestCase):
  """Convert the headspace code to C."""

  def test_converts_hello_world(self):
    """Hello World program"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    executable_path = os.path.join('tests', 'test_output', 'hello_test')
    with open(file_path, 'w') as c_source:
      c_source.write(files[0].content)
    # Then compile and run the c code.
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic', 
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', '-o',
                    executable_path, file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', executable_path], check=True)


if __name__ == '__main__':
  unittest.main()

