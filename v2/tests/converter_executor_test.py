import unittest
import parser
import converter
import os
import pathlib
import subprocess


HELLO_WORLD_EXAMPLE = """
moduleName = "jeffscudder.com/headspace/tests/hello"

main: function: void[][
  os.print["Hello World\\n"]
]
"""


FOREIGN_CODE_EXAMPLE = """
moduleName = "jeffscudder.com/headspace/tests/foreign"

main: function: void[][
BEGIN_FOREIGN_CODE_C
  char* hello_str = "hello\\n";
END_FOREIGN_CODE_C
BEGIN_FOREIGN_CODE_PYTHON
  hello_str = 'hello\\n'
END_FOREIGN_CODE_PYTHON
BEGIN_FOREIGN_CODE_GO
\tvar hello_str = "hello\\n"
END_FOREIGN_CODE_GO
BEGIN_FOREIGN_CODE_JAVA
    String hello_str = "hello\\n";
END_FOREIGN_CODE_JAVA
BEGIN_FOREIGN_CODE_JS
  const hello_str = "hello\\n";
END_FOREIGN_CODE_JS
BEGIN_FOREIGN_CODE_DOTNET
      string hello_str = "hello\\n";
END_FOREIGN_CODE_DOTNET
  os.print[hello_str]
]
"""


FUNCTION_CALLING_EXAMPLE = """
moduleName = "jeffscudder.com/headspace/tests/functions"

addNumbers: function: int32[a:int32, b:int32][
  return a + b
]

main: function: void[][
  os.printInt[addNumbers[5, 5]]
  os.print["\\n"]
]
"""


IF_ELSE_EXAMPLE = """
moduleName = "jeffscudder.com/headspace/tests/ifelse"

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
moduleName = "jeffscudder.com/headspace/tests/while"

main:function:void[][
  counter:int32
  counter = 0
  os.print["Counting up to 5:\\n"]
  while[counter < 5][
    counter++
    os.printInt[counter]
    os.print["\\n"]
  ]
]
"""


class TestConvertToCAndExecute(unittest.TestCase):
  """Convert the headspace code to C."""

  def test_converts_hello_world(self):
    """Hello World program in C."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    executable_path = os.path.join(compilation_directory, 'hello_test')
    c_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    c_file_path.parent.mkdir(parents=True, exist_ok=True)
    c_file_path.write_text(files[0].content)
    h_file_path = pathlib.Path(os.path.join(compilation_directory, files[1].filename))
    h_file_path.parent.mkdir(parents=True, exist_ok=True)
    h_file_path.write_text(files[1].content)
    # Then compile and run the C code.
    include_path_arg = '-I' + compilation_directory
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', include_path_arg, '-o',
                    executable_path, c_file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', c_file_path], check=True)
    subprocess.run(['rm', h_file_path], check=True)
    subprocess.run(['rm', executable_path], check=True)

  def test_converts_foreign_code(self):
    """Example of including foreign code for C."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    executable_path = os.path.join(compilation_directory, 'foreign')
    c_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    c_file_path.parent.mkdir(parents=True, exist_ok=True)
    c_file_path.write_text(files[0].content)
    h_file_path = pathlib.Path(os.path.join(compilation_directory, files[1].filename))
    h_file_path.parent.mkdir(parents=True, exist_ok=True)
    h_file_path.write_text(files[1].content)
    # Then compile and run the C code.
    include_path_arg = '-I' + compilation_directory
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', include_path_arg, '-o',
                    executable_path, c_file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    subprocess.run(['rm', c_file_path], check=True)
    subprocess.run(['rm', h_file_path], check=True)
    subprocess.run(['rm', executable_path], check=True)

  def test_converts_function_calls(self):
    """Example of defining and calling a function for C."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    executable_path = os.path.join(compilation_directory, 'functions')
    c_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    c_file_path.parent.mkdir(parents=True, exist_ok=True)
    c_file_path.write_text(files[0].content)
    h_file_path = pathlib.Path(os.path.join(compilation_directory, files[1].filename))
    h_file_path.parent.mkdir(parents=True, exist_ok=True)
    h_file_path.write_text(files[1].content)
    # Then compile and run the C code.
    include_path_arg = '-I' + compilation_directory
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', include_path_arg, '-o',
                    executable_path, c_file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'10\n', result.stdout)
    subprocess.run(['rm', c_file_path], check=True)
    subprocess.run(['rm', h_file_path], check=True)
    subprocess.run(['rm', executable_path], check=True)

  def test_converts_while_statements(self):
    """Example of while statements for C."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    executable_path = os.path.join(compilation_directory, 'while_statements')
    c_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    c_file_path.parent.mkdir(parents=True, exist_ok=True)
    c_file_path.write_text(files[0].content)
    h_file_path = pathlib.Path(os.path.join(compilation_directory, files[1].filename))
    h_file_path.parent.mkdir(parents=True, exist_ok=True)
    h_file_path.write_text(files[1].content)
    # Then compile and run the C code.
    include_path_arg = '-I' + compilation_directory
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', include_path_arg, '-o',
                    executable_path, c_file_path], check=True)
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'Counting up to 5:\n1\n2\n3\n4\n5\n', result.stdout)
    subprocess.run(['rm', c_file_path], check=True)
    subprocess.run(['rm', h_file_path], check=True)
    subprocess.run(['rm', executable_path], check=True)


class TestConvertToPythonAndExecute(unittest.TestCase):
  """Convert the headspace code to Python."""

  def test_converts_hello_world(self):
    """Hello World program in Python."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(3, len(files))
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
    self.assertEqual(3, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as py_source:
      py_source.write(files[0].content)
    # Then execute the Python code.
    result = subprocess.run(['python3', file_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)


class TestConvertToGoAndExecute(unittest.TestCase):
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

  def test_converts_foreign_code(self):
    """Example of including foreign code for Go."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    package_path = os.path.join('tests', 'test_output', 'foreign')
    subprocess.run(['mkdir', package_path], check=True)
    with open(file_path, 'w') as go_source:
      go_source.write(files[0].content)
    # Execute the Go code.
    result = subprocess.run(['go', 'run', file_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rmdir', package_path], check=True)

  def test_converts_function_calls(self):
    """Example of defining and calling a function for Go."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    package_path = os.path.join('tests', 'test_output', 'functions')
    subprocess.run(['mkdir', package_path], check=True)
    with open(file_path, 'w') as go_source:
      go_source.write(files[0].content)
    # Execute the Go code.
    result = subprocess.run(['go', 'run', file_path], check=True, capture_output=True)
    self.assertEqual(b'10\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rmdir', package_path], check=True)

  def test_converts_if_else(self):
    """Example of if-else statements for Go."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    package_path = os.path.join('tests', 'test_output', 'ifelse')
    subprocess.run(['mkdir', package_path], check=True)
    with open(file_path, 'w') as go_source:
      go_source.write(files[0].content)
    # Execute the Go code.
    result = subprocess.run(['go', 'run', file_path], check=True, capture_output=True)
    self.assertEqual(b'Yes, a is 5.\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rmdir', package_path], check=True)

  def test_converts_while_statements(self):
    """Example of while statements for Go."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    package_path = os.path.join('tests', 'test_output', 'while')
    subprocess.run(['mkdir', package_path], check=True)
    with open(file_path, 'w') as go_source:
      go_source.write(files[0].content)
    # Execute the Go code.
    result = subprocess.run(['go', 'run', file_path], check=True, capture_output=True)
    self.assertEqual(b'Counting up to 5:\n1\n2\n3\n4\n5\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rmdir', package_path], check=True)


class TestConvertToJavaScriptAndExecute(unittest.TestCase):
  """Convert the headspace code to JavaScript."""

  def test_converts_hello_world(self):
    """Hello World program in JavaScript"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(2, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as js_source:
      js_source.write(files[0].content)
    # Then execute the JavaScript code using Node.
    result = subprocess.run(['node', file_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)

  def test_converts_foreign_code(self):
    """Example of including foreign code for JavaScript."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(2, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as js_source:
      js_source.write(files[0].content)
    # Then execute the JavaScript code using Node.
    result = subprocess.run(['node', file_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)

  def test_converts_function_calls(self):
    """Example of defining and calling a function for JavaScript."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(2, len(files))
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    with open(file_path, 'w') as js_source:
      js_source.write(files[0].content)
    package_file_path = os.path.join('tests', 'test_output', files[1].filename)
    with open(package_file_path, 'w') as package_source:
      package_source.write(files[1].content)
    # Then execute the JavaScript code using Node.
    result = subprocess.run(['node', file_path], check=True, capture_output=True)
    self.assertEqual(b'10\n', result.stdout)
    subprocess.run(['rm', file_path], check=True)
    subprocess.run(['rm', package_file_path], check=True)

class TestConvertToJavaAndExecute(unittest.TestCase):
  """Convert the headspace code to Java."""

  def test_converts_hello_world(self):
    """Hello World program in Java"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(1, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    file_path = os.path.join('tests', 'test_output', files[0].filename)
    java_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    java_file_path.parent.mkdir(parents=True, exist_ok=True)
    java_file_path.write_text(files[0].content)
    java_class_path = '.'
    # Then execute the Java code using javac then java.
    result = subprocess.run(['javac', java_file_path], check=True, capture_output=True)
    os.chdir(os.path.join('tests', 'test_output'))
    # Run the program as java Hello (minus the .java)
    class_file_name = '.'.join(str(java_file_path).split('/')[2:])[:-5]
    result = subprocess.run(['java', '-cp', java_class_path, class_file_name], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    # Move back to the test running directory.
    os.chdir(os.path.join('..', '..'))
    # Delete both the .java and .class file for the hello world program.
    subprocess.run(['rm', java_file_path], check=True)
    subprocess.run(['rm', str(java_file_path)[:-5] + '.class'], check=True)

  def test_converts_foreign_code(self):
    """Example of including foreign code for Java."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(1, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    java_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    java_file_path.parent.mkdir(parents=True, exist_ok=True)
    java_file_path.write_text(files[0].content)
    java_class_path = '.'
    # Then execute the Java code using javac then java.
    result = subprocess.run(['javac', java_file_path], check=True, capture_output=True)
    os.chdir(os.path.join('tests', 'test_output'))
    # Run the program as java com....Foreign (minus the .java)
    class_file_name = '.'.join(str(java_file_path).split('/')[2:])[:-5]
    result = subprocess.run(['java', '-cp', java_class_path, class_file_name], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    # Move back to the test running directory.
    os.chdir(os.path.join('..', '..'))
    # Delete both the .java and .class file for the hello world program.
    subprocess.run(['rm', java_file_path], check=True)
    subprocess.run(['rm', str(java_file_path)[:-5] + '.class'], check=True)


class TestConvertToDotNetAndExecute(unittest.TestCase):
  """Convert the headspace code to .NET (C#)."""

  def test_converts_hello_world(self):
    """Hello World program in .NET (C#)."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(1, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    dotnet_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    dotnet_file_path.parent.mkdir(parents=True, exist_ok=True)
    dotnet_file_path.write_text(files[0].content)
    # Then execute the .NET code using dotnet run.
    result = subprocess.run(['dotnet', 'run', dotnet_file_path], check=True, capture_output=True)
    self.assertEqual(b'Hello World\n', result.stdout)
    # Delete the .cs file for the hello world program.
    subprocess.run(['rm', dotnet_file_path], check=True)

  def test_converts_foreign_code(self):
    """Example of including foreign code for .NET (C#)."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(1, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    dotnet_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    dotnet_file_path.parent.mkdir(parents=True, exist_ok=True)
    dotnet_file_path.write_text(files[0].content)
    # Then execute the .NET code using dotnet run.
    result = subprocess.run(['dotnet', 'run', dotnet_file_path], check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)
    # Delete the .cs file for the hello world program.
    subprocess.run(['rm', dotnet_file_path], check=True)

  def test_converts_function_calls(self):
    """Example of defining and calling a function for .NET (C#)."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(1, len(files))
    compilation_directory = os.path.join('tests', 'test_output')
    dotnet_file_path = pathlib.Path(os.path.join(compilation_directory, files[0].filename))
    dotnet_file_path.parent.mkdir(parents=True, exist_ok=True)
    dotnet_file_path.write_text(files[0].content)
    # Then execute the .NET code using dotnet run.
    result = subprocess.run(['dotnet', 'run', dotnet_file_path], check=True, capture_output=True)
    self.assertEqual(b'10\n', result.stdout)
    # Delete the .cs file for the hello world program.
    subprocess.run(['rm', dotnet_file_path], check=True)


if __name__ == '__main__':
  unittest.main()

