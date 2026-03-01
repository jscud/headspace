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


FOREIGN_CODE_EXAMPLE = """
moduleName = "foreign"

main: function[][
BEGIN_FOREIGN_CODE_C
  char* hello_str = "hello\\n";
END_FOREIGN_CODE_C
BEGIN_FOREIGN_CODE_PYTHON
  hello_str = 'hello\\n'
END_FOREIGN_CODE_PYTHON
  os.print[hello_str]
]
"""


class TestConvertToC(unittest.TestCase):
  """Convert the headspace code to C."""

  def test_converts_hello_world(self):
    """Hello World program in C"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    executable_path = os.path.join('tests', 'test_output', 'hello_test')
    with open(file_path, 'w') as c_source:
      c_source.write(files[0].content)
    # Then compile and run the C code.
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', '-o',
                    executable_path, file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rm', executable_path], check=True)

  def test_converts_foreign_code(self):
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    executable_path = os.path.join('tests', 'test_output', 'foreign')
    with open(file_path, 'w') as c_source:
      c_source.write(files[0].content)
    # Then compile and run the C code.
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', '-o',
                    executable_path, file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rm', executable_path], check=True)


class TestConvertToPython(unittest.TestCase):
  """Convert the headspace code to Python."""

  def test_converts_hello_world(self):
    """Hello World program in Python."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as py_source:
      py_source.write(files[0].content)
    # Then execute the Python code.
    result = subprocess.run(['python3', file_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)

  def test_converts_foreign_code(self):
    """Example of including foreign code for Python."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as py_source:
      py_source.write(files[0].content)
    # Then execute the Python code.
    result = subprocess.run(['python3', file_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)


class TestConvertToGo(unittest.TestCase):
  """Convert the headspace code to Go."""

  def test_converts_hello_world(self):
    """Hello World program in Go"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    package_path = os.path.join('tests', 'test_output', 'hello')
    subprocess.run(['mkdir', package_path], check=True)
    with open(file_path, 'w') as go_source:
      go_source.write(files[0].content)
    # Execute the Go code.
    result = subprocess.run(['go', 'run', file_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rmdir', package_path], check=True)


class TestConvertToJavaScript(unittest.TestCase):
  """Convert the headspace code to JavaScript."""

  def test_converts_hello_world(self):
    """Hello World program in JavaScript"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as js_source:
      js_source.write(files[0].content)
    # Then execute the JavaScript code using Node.
    result = subprocess.run(['node', file_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)


class TestConvertToJava(unittest.TestCase):
  """Convert the headspace code to Java."""

  def test_converts_hello_world(self):
    """Hello World program in Java"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as java_source:
      java_source.write(files[0].content)
    # Then execute the Java code using javac then java.
    result = subprocess.run(['javac', file_path], check=True, capture_output=True)
    os.chdir(os.path.join('tests', 'test_output'))
    # Run the program as java Hello (minus the .java)
    class_file_name = os.path.split(file_path)[-1][:-5]
    result = subprocess.run(['java', class_file_name], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    # Move back to the test running directory.
    os.chdir(os.path.join('..', '..'))
    # Delete both the .java and .class file for the hello world program.
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rm', file_path[:-5] + '.class'], check=True)


class TestConvertToDotNet(unittest.TestCase):
  """Convert the headspace code to .NET (C#)."""

  def test_converts_hello_world(self):
    """Hello World program in .NET (C#)"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as dotnet_source:
      dotnet_source.write(files[0].content)
    # Then execute the .NET code using dotnet run.
    result = subprocess.run(['dotnet', 'run', file_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    # Delete the .cs file for the hello world program.
    subprocess.run(['rm', file_path], check=True)


if __name__ == '__main__':
  unittest.main()

