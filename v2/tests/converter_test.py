import unittest
import parser
import converter
import os
import subprocess

"""Similar to Converter Tests, but doesn't execute the compilation and
running of external programs."""


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
moduleName = "functions"

addNumbers: function[a:int32, b:int32][
  return a + b
]

main: function[][
  os.print[text.intToStr[addNumbers[5, 5], 10]]
  os.print["\\n"]
]
"""


class TestConvertToC(unittest.TestCase):
  """Convert the headspace code to C."""

  def test_converts_hello_world(self):
    """Hello World program in C."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    self.assertTrue('.c' in files[0].filename)
    self.assertTrue('int main(' in files[0].content)
    self.assertTrue('printf("%s", "Hello World\\n")' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for C."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    self.assertTrue('char* hello_str = "hello\\n";' in files[0].content)
    self.assertTrue('printf("%s", hello_str);' in files[0].content)
    self.assertFalse('var hello_str = "hello\\n"' in files[0].content)

  def test_function_calling(self):
    """Example of including function calls for C."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    #tree.print()
    files = converter.convert(tree, 'c')
    #print(files[0].content)
    self.assertEqual(2, len(files))


class TestConvertToPython(unittest.TestCase):
  """Convert the headspace code to Python."""

  def test_converts_hello_world(self):
    """Hello World program in Python."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(1, len(files))
    self.assertTrue('.py' in files[0].filename)
    self.assertTrue('def main():' in files[0].content)
    self.assertTrue('print("Hello World\\n", end="")' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for Python."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(1, len(files))
    self.assertTrue('hello_str = \'hello\\n\'' in files[0].content)
    self.assertTrue('print(hello_str, end="")' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)


class TestConvertToGo(unittest.TestCase):
  """Convert the headspace code to Go."""

  def test_converts_hello_world(self):
    """Hello World program in Go"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    self.assertTrue('.go' in files[0].filename)
    self.assertTrue('func main() {' in files[0].content)
    self.assertTrue('fmt.Print("Hello World\\n")' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for Go."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    self.assertTrue('var hello_str = "hello\\n"' in files[0].content)
    self.assertTrue('fmt.Print(hello_str)' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)


class TestConvertToJavaScript(unittest.TestCase):
  """Convert the headspace code to JavaScript."""

  def test_converts_hello_world(self):
    """Hello World program in JavaScript"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(1, len(files))
    self.assertTrue('.js' in files[0].filename)
    self.assertTrue('function main() {' in files[0].content)
    self.assertTrue('process.stdout.write("Hello World\\n");' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for JavaScript."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(1, len(files))
    self.assertTrue('const hello_str = "hello\\n";' in files[0].content)
    self.assertTrue('process.stdout.write(hello_str);' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)

class TestConvertToJava(unittest.TestCase):
  """Convert the headspace code to Java."""

  def test_converts_hello_world(self):
    """Hello World program in Java"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(1, len(files))
    self.assertTrue('.java' in files[0].filename)
    self.assertTrue('public static void main(String[] args)' in files[0].content)
    self.assertTrue('System.out.print("Hello World\\n");' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for Java."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(1, len(files))
    self.assertTrue('String hello_str = "hello\\n";' in files[0].content)
    self.assertTrue('System.out.print(hello_str);' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)


class TestConvertToDotNet(unittest.TestCase):
  """Convert the headspace code to .NET (C#)."""

  def test_converts_hello_world(self):
    """Hello World program in .NET (C#)."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(1, len(files))
    self.assertTrue('.cs' in files[0].filename)
    self.assertTrue('static void Main(string[] args) {' in files[0].content)
    self.assertTrue('Console.Write("Hello World\\n");' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for .NET (C#)."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(1, len(files))
    self.assertTrue('string hello_str = "hello\\n";' in files[0].content)
    self.assertTrue('Console.Write(hello_str);' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)


if __name__ == '__main__':
  unittest.main()

