import unittest
import builder
import os
import subprocess


CLEANUP_GENERATED_SOURCE = True


class TestBuildCAndExecute(unittest.TestCase):
  """Build a headspace project, converting to C."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'c')
    # Compile the library source.
    compilation_directory = os.path.join('tests', 'test_projects', 'import_example', 'c')
    library_source_path = os.path.join(compilation_directory, 'tests', 'projects', 'library.c')
    library_header_path = os.path.join(compilation_directory, 'tests', 'projects', 'library.h')
    compiled_library_path = os.path.join(compilation_directory, 'tests', 'projects', 'library.o')
    include_path_arg = '-I' + compilation_directory
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', include_path_arg, '-c',
                    library_source_path, '-o', compiled_library_path], check=True)
    # Compile the main function.
    binary_source_path = os.path.join(compilation_directory, 'tests', 'projects', 'useLibrary.c')
    binary_header_path = os.path.join(compilation_directory, 'tests', 'projects', 'useLibrary.h')
    executable_path = os.path.join(compilation_directory, 'tests', 'projects', 'useLibrary')
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', include_path_arg, '-o',
                    executable_path, binary_source_path, compiled_library_path], check=True)
    # Run the program that includes the import.
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    if CLEANUP_GENERATED_SOURCE:
      subprocess.run(['rm', library_source_path], check=True)
      subprocess.run(['rm', library_header_path], check=True)
      subprocess.run(['rm', compiled_library_path], check=True)
      subprocess.run(['rm', binary_source_path], check=True)
      subprocess.run(['rm', binary_header_path], check=True)
      subprocess.run(['rm', executable_path], check=True)


class TestBuildPythonAndExecute(unittest.TestCase):
  """Build a headspace project, converting to Python."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'python')
    library_source_path = os.path.join('tests', 'test_projects', 'import_example', 'python', 'tests', 'projects', 'library.py')
    executable_source_path = os.path.join('tests', 'test_projects', 'import_example', 'python', 'tests', 'projects', 'useLibrary.py')
    # Run the program that includes the import.
    # Set the PYTHONPATH to point to the project's root directory that contains the library packages.
    test_env = os.environ.copy()
    test_env['PYTHONPATH'] = os.path.join('tests', 'test_projects', 'import_example', 'python')
    result = subprocess.run(['python3', executable_source_path], env=test_env, check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    if CLEANUP_GENERATED_SOURCE:
      subprocess.run(['rm', library_source_path], check=True)
      subprocess.run(['rm', executable_source_path], check=True)


class TestBuildGoAndExecute(unittest.TestCase):
  """Build a headspace project, converting to Go."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'go')
    go_mod_directory_path = os.path.join('tests', 'test_projects', 'import_example', 'go')
    library_source_path = os.path.join('tests', 'test_projects', 'import_example', 'go', 'library.go')
    executable_source_path = os.path.join('tests', 'test_projects', 'import_example', 'python', 'useLibrary', 'main.go')
    # Generate the go module.
    os.chdir(go_mod_directory_path)
    subprocess.run(['go', 'mod', 'init', 'testsprojects'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Run the program that includes the import.
    result = subprocess.run(['go', 'run', os.path.join('useLibrary', 'main.go')], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    if CLEANUP_GENERATED_SOURCE:
      subprocess.run(['rm', 'go.mod'], check=True)
      subprocess.run(['rm', 'library.go'], check=True)
      subprocess.run(['rm', os.path.join('useLibrary', 'main.go')], check=True)
    os.chdir(os.path.join('..', '..', '..', '..'))


class TestBuildJavaScriptAndExecute(unittest.TestCase):
  """Build a headspace project, converting to JavaScript."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'javascript')
    library_source_path = os.path.join('tests', 'test_projects', 'import_example', 'javascript', 'library.js')
    executable_source_path = os.path.join('tests', 'test_projects', 'import_example', 'javascript', 'useLibrary.js')
    package_source_path = os.path.join('tests', 'test_projects', 'import_example', 'javascript', 'package.json')
    # Run the program that includes the import.
    result = subprocess.run(['node', executable_source_path], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    if CLEANUP_GENERATED_SOURCE:
      subprocess.run(['rm', library_source_path], check=True)
      subprocess.run(['rm', executable_source_path], check=True)
      subprocess.run(['rm', package_source_path], check=True)


class TestBuildJavaAndExecute(unittest.TestCase):
  """Build a headspace project, converting to Java."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'java')
    # Compile the library source.
    compilation_directory = os.path.join('tests', 'test_projects', 'import_example', 'java')
    os.chdir(compilation_directory)
    library_source_path = os.path.join('com', 'jeffscudder', 'tests', 'projects', 'Library.java')
    use_library_source_path = os.path.join('com', 'jeffscudder', 'tests', 'projects', 'UseLibrary.java')
    compiled_use_library_class = 'com.jeffscudder.tests.projects.UseLibrary'
    subprocess.run(['javac', '-d', '.', library_source_path], check=True)
    # Compile the main function.
    subprocess.run(['javac', '-d', '.', use_library_source_path], check=True)
    # Run the program that includes the import.
    result = subprocess.run(['java', compiled_use_library_class], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    if CLEANUP_GENERATED_SOURCE:
      subprocess.run(['rm', library_source_path], check=True)
      subprocess.run(['rm', use_library_source_path], check=True)
      subprocess.run(['rm', os.path.join('com', 'jeffscudder', 'tests', 'projects', 'Library.class')], check=True)
      subprocess.run(['rm', os.path.join('com', 'jeffscudder', 'tests', 'projects', 'UseLibrary.class')], check=True)
    os.chdir(os.path.join('..', '..', '..', '..'))


class TestBuildDotNetAndExecute(unittest.TestCase):
  """Build a headspace project, converting to .NET (C#)."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'dotnet')
    # Compile the library source.
    compilation_directory = os.path.join('tests', 'test_projects', 'import_example', 'dotnet', 'Tests.Projects')
    os.chdir(compilation_directory)
    result = subprocess.run(['dotnet', 'run'], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    if CLEANUP_GENERATED_SOURCE:
      subprocess.run(['rm', 'headspace.csproj'], check=True)
      subprocess.run(['rm', 'Library.cs'], check=True)
      subprocess.run(['rm', 'UseLibrary.cs'], check=True)
      subprocess.run(['rm', '-r', 'bin'], check=True)
      subprocess.run(['rm', '-r', 'obj'], check=True)
    os.chdir(os.path.join('..', '..', '..', '..', '..'))


if __name__ == '__main__':
  unittest.main()

