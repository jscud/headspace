import unittest
import parser
import converter
import os
import subprocess

"""Similar to Converter Tests, but doesn't execute the compilation and
running of external programs."""


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

IMPORTS_EXAMPLE = """
import "jeffscudder.com/headspace/tests/moduleA" as moduleA

moduleName = "jeffscudder.com/headspace/tests/imports"

import "jeffscudder.com/headspace/tests/moduleB" as moduleB

main:function:void[][
  os.print["I have imports.\\n"]
]
"""

# Uses the data class as a local stack variable (struct in C and Go).
DATA_CLASS_EXAMPLE = """
moduleName = "jeffscudder.com/headspace/tests/dataclassdemo"

DataClass: class [
  x: int
]

main: function: void[][
  instance:DataClass
  new[instance]
  instance.x = 42
  os.print["Class member x: "]
  os.printInt[instance.x]
  os.print["\\n"]
]
"""

# Uses the data class as a refernce to a heap instance (pointer in C).
CLASS_REF_EXAMPLE = """
moduleName = "jeffscudder.com/headspace/tests/classref"

DataClass: class [
  x: int
]

main: function: void[][
  instance:reference:DataClass
  allocate[instance]
  instance.x = 42
  os.print["Class member x: "]
  os.printInt[instance.x]
  os.print["\\n"]
  release[instance]
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
    files = converter.convert(tree, 'c')
    self.assertEqual(2, len(files))
    # Check function signature in .h file.
    self.assertTrue('int32_t functions_addNumbers(int32_t a, int32_t b);' in files[1].content)
    # Check funciton definition in .c file.
    self.assertTrue('int32_t functions_addNumbers(int32_t a, int32_t b)' in files[0].content)
    self.assertTrue('  return a + b;' in files[0].content)
    self.assertTrue('  printf("%d", functions_addNumbers(5 ,5));' in files[0].content)

  def test_if_else(self):
    """Example of including if-else statements for C."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertTrue('int32_t a;' in files[0].content)
    self.assertTrue('a = 5;' in files[0].content)
    self.assertTrue('if(a == 5)' in files[0].content)
    self.assertTrue('printf("%s", "Yes, a is 5.\\n");' in files[0].content)
    self.assertTrue('else' in files[0].content)
    self.assertTrue('printf("%s", "No, a is not 5.\\n");' in files[0].content)

  def test_while(self):
    """Example of including while statements for C."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertTrue('while(counter < 5)' in files[0].content)
    self.assertTrue('counter++;' in files[0].content)

  def test_imports(self):
    """Example of using import statements with C."""
    tree = parser.parse_source(IMPORTS_EXAMPLE)
    files = converter.convert(tree, 'c')
    self.assertTrue('#include"headspace/tests/moduleA.h"' in files[0].content)
    self.assertTrue('#include"headspace/tests/moduleB.h"' in files[0].content)
    self.assertTrue('#include"headspace/tests/moduleA.h"' in files[1].content)
    self.assertTrue('#include"headspace/tests/moduleB.h"' in files[1].content)

  def test_data_class(self):
    """Example of declaring and using a class reference with C."""
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    files = converter.convert(tree, 'c')
    # Check .c file contents.
    self.assertTrue('dataclassdemo_DataClass* dataclassdemo_DataClass_constructor(void) {' in files[0].content)
    self.assertTrue('  return malloc(sizeof(dataclassdemo_DataClass));' in files[0].content)
    self.assertTrue('  dataclassdemo_DataClass instance;' in files[0].content)
    self.assertTrue('  dataclassdemo_DataClass_init(&instance);' in files[0].content)
    self.assertTrue('  instance.x = 42;' in files[0].content)
    self.assertTrue('  printf("%d", instance.x);' in files[0].content)
    self.assertFalse('  classref_DataClass* instance;' in files[0].content)
    self.assertFalse('  instance->x = 42;' in files[0].content)
    self.assertFalse('  printf("%d", instance->x);' in files[0].content)
    self.assertFalse('  free(instance);' in files[0].content)
    # Check .h file contents.
    self.assertTrue('typedef struct {' in files[1].content)
    self.assertTrue('  int x;' in files[1].content)
    self.assertTrue('} dataclassdemo_DataClass;' in files[1].content)
    self.assertTrue('void dataclassdemo_DataClass_init(dataclassdemo_DataClass* this);' in files[1].content)
    self.assertTrue('dataclassdemo_DataClass* dataclassdemo_DataClass_constructor(void);' in files[1].content)

  def test_class_ref(self):
    """Example of declaring and using a class reference with C."""
    tree = parser.parse_source(CLASS_REF_EXAMPLE)
    files = converter.convert(tree, 'c')
    # Check .c file contents.
    self.assertTrue('  classref_DataClass* instance;' in files[0].content)
    self.assertTrue('  instance = classref_DataClass_constructor();' in files[0].content)
    self.assertTrue('  instance->x = 42;' in files[0].content)
    self.assertTrue('  printf("%d", instance->x);' in files[0].content)
    self.assertTrue('  free(instance);' in files[0].content)
    self.assertFalse('  classref_DataClass instance;' in files[0].content)
    self.assertFalse('  instance.x = 42;' in files[0].content)
    self.assertFalse('  printf("%d", instance.x);' in files[0].content)
    # Check .h file contents.
    self.assertTrue('void classref_DataClass_init(classref_DataClass* this);' in files[1].content)
    self.assertTrue('classref_DataClass* classref_DataClass_constructor(void);' in files[1].content)


class TestConvertToPython(unittest.TestCase):
  """Convert the headspace code to Python."""

  def test_converts_hello_world(self):
    """Hello World program in Python."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(3, len(files))  # Note this includes __init__.py files.
    self.assertTrue('.py' in files[0].filename)
    self.assertTrue('def main():' in files[0].content)
    self.assertTrue('print("Hello World\\n", end="")' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for Python."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(3, len(files))
    self.assertTrue('hello_str = \'hello\\n\'' in files[0].content)
    self.assertTrue('print(hello_str, end="")' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)

  def test_function_calling(self):
    """Example of including function calls for Python."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertEqual(3, len(files))
    self.assertTrue('def addNumbers(a: int, b: int) -> int:' in files[0].content)
    self.assertTrue('  return a + b' in files[0].content)
    self.assertTrue('  print(addNumbers(5 ,5), end="")' in files[0].content)

  def test_if_else(self):
    """Example of including if-else statements for Python."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertTrue('  a = 5' in files[0].content)
    self.assertTrue('  if a == 5:' in files[0].content)
    self.assertTrue('    print("Yes, a is 5.\\n", end="")' in files[0].content)
    self.assertTrue('  else:' in files[0].content)
    self.assertTrue('    print("No, a is not 5.\\n", end="")' in files[0].content)

  def test_while(self):
    """Example of including while statements for Python."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertTrue('  while counter < 5:' in files[0].content)
    self.assertTrue('    counter += 1' in files[0].content)

  def test_data_class(self):
    """Example of declaring and using a class with Python."""
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertTrue('class DataClass:' in files[0].content)
    self.assertTrue('  def __init__(self):' in files[0].content)
    self.assertTrue('    self.x = None' in files[0].content)
    self.assertTrue('  instance = DataClass()' in files[0].content)
    self.assertTrue('  instance.x = 42' in files[0].content)
    self.assertFalse('  del instance' in files[0].content)

  def test_class_ref(self):
    """Example of declaring and using a class reference with Python."""
    tree = parser.parse_source(CLASS_REF_EXAMPLE)
    files = converter.convert(tree, 'python')
    self.assertTrue('  instance = DataClass()' in files[0].content)
    self.assertTrue('  instance.x = 42' in files[0].content)
    self.assertTrue('  del instance' in files[0].content)


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

  def test_function_calling(self):
    """Example of including function calls for Go."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertEqual(1, len(files))
    self.assertTrue('func AddNumbers(a int32, b int32) int32 {' in files[0].content)
    self.assertTrue('\treturn a + b' in files[0].content)
    self.assertTrue('\tfmt.Printf("%d", AddNumbers(5 ,5))' in files[0].content)

  def test_if_else(self):
    """Example of including if-else statements for Go."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertTrue('\tvar a int32' in files[0].content)
    self.assertTrue('\ta = 5' in files[0].content)
    self.assertTrue('\tif a == 5 {' in files[0].content)
    self.assertTrue('\t\tfmt.Print("Yes, a is 5.\\n")' in files[0].content)
    self.assertTrue('\t} else {' in files[0].content)
    self.assertTrue('\t\tfmt.Print("No, a is not 5.\\n")' in files[0].content)

  def test_while(self):
    """Example of including while statements for Go."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertTrue('\tfor counter < 5' in files[0].content)
    self.assertTrue('\t\tcounter++' in files[0].content)

  def test_data_class(self):
    """Example of declaring and using a class with Go."""
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertTrue('type DataClass struct {' in files[0].content)
    self.assertTrue('\tX int' in files[0].content)
    self.assertTrue('\tvar instance DataClass' in files[0].content)
    self.assertTrue('\tinstance = DataClass{}' in files[0].content)
    self.assertTrue('\tinstance.X = 42' in files[0].content)
    self.assertTrue('\tfmt.Printf("%d", instance.X)' in files[0].content)

  def test_class_ref(self):
    """Example of declaring and using a class reference with Go."""
    tree = parser.parse_source(CLASS_REF_EXAMPLE)
    files = converter.convert(tree, 'go')
    self.assertTrue('\tvar instance *DataClass' in files[0].content)
    self.assertTrue('\tinstance = new(DataClass)' in files[0].content)
    self.assertTrue('\tinstance = nil' in files[0].content)


class TestConvertToJavaScript(unittest.TestCase):
  """Convert the headspace code to JavaScript."""

  def test_converts_hello_world(self):
    """Hello World program in JavaScript"""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(2, len(files))
    self.assertTrue('.js' in files[0].filename)
    self.assertTrue('function main() {' in files[0].content)
    self.assertTrue('process.stdout.write("Hello World\\n");' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for JavaScript."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(2, len(files))
    self.assertTrue('const hello_str = "hello\\n";' in files[0].content)
    self.assertTrue('process.stdout.write(hello_str);' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)

  def test_function_calling(self):
    """Example of including function calls for JavaScript."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertEqual(2, len(files))
    self.assertTrue(' * @param {number} a' in files[0].content)
    self.assertTrue(' * @param {number} b' in files[0].content)
    self.assertTrue(' * @returns {number}' in files[0].content)
    self.assertTrue('function addNumbers(a, b) {' in files[0].content)
    self.assertTrue('process.stdout.write("" + addNumbers(5 ,5));' in files[0].content)

  def test_if_else(self):
    """Example of including if-else statements for JavaScript."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertTrue('  let a;' in files[0].content)
    self.assertTrue('  a = 5;' in files[0].content)
    self.assertTrue('  if (a == 5) {' in files[0].content)
    self.assertTrue('    process.stdout.write("Yes, a is 5.\\n");' in files[0].content)
    self.assertTrue('  } else {' in files[0].content)
    self.assertTrue('    process.stdout.write("No, a is not 5.\\n");' in files[0].content)

  def test_while(self):
    """Example of including while statements for JavaScript."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertTrue('while (counter < 5) {' in files[0].content)
    self.assertTrue('counter++;' in files[0].content)

  def test_data_class(self):
    """Example of declaring and using a class with JavaScript."""
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertTrue('class DataClass {' in files[0].content)
    self.assertTrue('  constructor() {' in files[0].content)
    self.assertTrue('    this.x = null;' in files[0].content)
    self.assertTrue('  instance = new DataClass();' in files[0].content)
    self.assertTrue('  instance.x = 42;' in files[0].content)
    self.assertTrue('  process.stdout.write("" + instance.x);' in files[0].content)
    self.assertFalse('  instance = null;' in files[0].content)

  def test_class_ref(self):
    """Example of declaring and using a class reference with JavaScript."""
    tree = parser.parse_source(CLASS_REF_EXAMPLE)
    files = converter.convert(tree, 'javascript')
    self.assertTrue('  instance = new DataClass();' in files[0].content)
    self.assertTrue('  instance.x = 42;' in files[0].content)
    self.assertTrue('  instance = null;' in files[0].content)


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

  def test_function_calling(self):
    """Example of including function calls for Java."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(1, len(files))
    self.assertTrue('  public static int addNumbers(int a, int b)' in files[0].content)
    self.assertTrue('    return a + b;' in files[0].content)
    self.assertTrue('    System.out.print(addNumbers(5 ,5));' in files[0].content)

  def test_if_else(self):
    """Example of including if-else statements for Java."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertTrue('    int a;' in files[0].content)
    self.assertTrue('    a = 5;' in files[0].content)
    self.assertTrue('    if (a == 5) {' in files[0].content)
    self.assertTrue('      System.out.print("Yes, a is 5.\\n");' in files[0].content)
    self.assertTrue('    } else {' in files[0].content)
    self.assertTrue('      System.out.print("No, a is not 5.\\n");' in files[0].content)

  def test_while(self):
    """Example of including while statements for Java."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertTrue('while (counter < 5) {' in files[0].content)
    self.assertTrue('counter++;' in files[0].content)

  def test_data_class(self):
    """Example of declaring and using a class with Java."""
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertEqual(2, len(files))
    # Checks for the class with main.
    self.assertTrue('import com.jeffscudder.headspace.tests.DataClass;' in files[0].content)
    self.assertTrue('    DataClass instance;' in files[0].content)
    self.assertTrue('    instance = new DataClass();' in files[0].content)
    self.assertTrue('    instance.setX(42);' in files[0].content)
    self.assertTrue('    System.out.print(instance.getX());' in files[0].content)
    # Checks for DataClass.java
    self.assertTrue('class DataClass {' in files[1].content)
    self.assertTrue('  private int x;' in files[1].content)
    self.assertTrue('  DataClass() {' in files[1].content)
    self.assertTrue('    x = 0;' in files[1].content)
    self.assertTrue('  int getX() {' in files[1].content)
    self.assertTrue('    return this.x;' in files[1].content)
    self.assertTrue('  void setX(int x) {' in files[1].content)
    self.assertTrue('    this.x = x;' in files[1].content)

  def test_class_ref(self):
    """Example of declaring and using a class reference with Java."""
    tree = parser.parse_source(CLASS_REF_EXAMPLE)
    files = converter.convert(tree, 'java')
    self.assertTrue('    DataClass instance;' in files[0].content)
    self.assertTrue('    instance = new DataClass();' in files[0].content)
    self.assertTrue('    instance.setX(42);' in files[0].content)
    self.assertTrue('    instance = null;' in files[0].content)


class TestConvertToDotNet(unittest.TestCase):
  """Convert the headspace code to .NET (C#)."""

  def test_converts_hello_world(self):
    """Hello World program in .NET (C#)."""
    tree = parser.parse_source(HELLO_WORLD_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(2, len(files))
    self.assertTrue('.cs' in files[0].filename)
    self.assertTrue('static void Main(string[] args) {' in files[0].content)
    self.assertTrue('Console.Write("Hello World\\n");' in files[0].content)

  def test_converts_foreign_code(self):
    """Example of including foreign code for .NET (C#)."""
    tree = parser.parse_source(FOREIGN_CODE_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(2, len(files))
    self.assertTrue('string hello_str = "hello\\n";' in files[0].content)
    self.assertTrue('Console.Write(hello_str);' in files[0].content)
    self.assertFalse('char* hello_str = "hello\\n";' in files[0].content)

  def test_function_calling(self):
    """Example of including function calls for .NET (C#)."""
    tree = parser.parse_source(FUNCTION_CALLING_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(2, len(files))
    self.assertTrue('    public static int addNumbers(int a, int b) {' in files[0].content)
    self.assertTrue('      return a + b;' in files[0].content)
    self.assertTrue('      Console.Write(addNumbers(5 ,5));' in files[0].content)

  def test_if_else(self):
    """Example of including if-else statements for .NET (C#)."""
    tree = parser.parse_source(IF_ELSE_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertTrue('      int a;' in files[0].content)
    self.assertTrue('      a = 5;' in files[0].content)
    self.assertTrue('      if (a == 5) {' in files[0].content)
    self.assertTrue('        Console.Write("Yes, a is 5.\\n");' in files[0].content)
    self.assertTrue('      } else {' in files[0].content)
    self.assertTrue('        Console.Write("No, a is not 5.\\n");' in files[0].content)

  def test_while(self):
    """Example of including while statements for .NET (C#)."""
    tree = parser.parse_source(WHILE_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertTrue('while (counter < 5) {' in files[0].content)
    self.assertTrue('counter++;' in files[0].content)

  def test_data_class(self):
    """Example of declaring and using a class with .NET (C#)."""
    tree = parser.parse_source(DATA_CLASS_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(3, len(files))
    # Checks for the class with main.
    self.assertTrue('      DataClass instance;' in files[0].content)
    self.assertTrue('      instance = new DataClass();' in files[0].content)
    self.assertTrue('      instance.x = 42;' in files[0].content)
    self.assertTrue('      Console.Write(instance.x);' in files[0].content)
    # Checks for DataClass.cs
    self.assertTrue('  class DataClass {' in files[2].content)
    self.assertTrue('    public int x { get; set; }' in files[2].content)
    self.assertTrue('    public DataClass() {' in files[2].content)

  def test_class_ref(self):
    """Example of declaring and using a class reference with .NET (C#)."""
    tree = parser.parse_source(CLASS_REF_EXAMPLE)
    files = converter.convert(tree, 'dotnet')
    self.assertEqual(3, len(files))
    # Checks for the class with main.
    self.assertTrue('      DataClass instance;' in files[0].content)
    self.assertTrue('      instance = new DataClass();' in files[0].content)
    self.assertTrue('      instance.x = 42;' in files[0].content)
    self.assertTrue('      Console.Write(instance.x);' in files[0].content)
    self.assertTrue('      instance = null;' in files[0].content)


if __name__ == '__main__':
  unittest.main()

