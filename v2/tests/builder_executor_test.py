import unittest
import builder
import os
import subprocess


class TestBuildCAndExecute(unittest.TestCase):
  """Build a headspace project, converting to C."""

  def test_imports_sample(self):
    """Multiple files which import and run."""
    builder.convert_project(os.path.join('tests', 'test_projects', 'import_example'), 'c')
    # Compile the library source.
    library_source_path = os.path.join('tests', 'test_projects', 'import_example', 'c', 'library.c')
    library_header_path = os.path.join('tests', 'test_projects', 'import_example', 'c', 'library.h')
    compiled_library_path = os.path.join('tests', 'test_projects', 'import_example', 'c', 'library.o')
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', '-c',
                    library_source_path, '-o', compiled_library_path], check=True)
    # Compile the main function.
    binary_source_path = os.path.join('tests', 'test_projects', 'import_example', 'c', 'useLibrary.c')
    binary_header_path = os.path.join('tests', 'test_projects', 'import_example', 'c', 'useLibrary.h')
    executable_path = os.path.join('tests', 'test_projects', 'import_example', 'c', 'useLibrary')
    subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                    '-Wmissing-prototypes', '-Wstrict-prototypes',
                    '-Wold-style-definition', '-o',
                    executable_path, binary_source_path, compiled_library_path], check=True)
    # Run the program that includes the import.
    result = subprocess.run([executable_path], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
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
    library_source_path = os.path.join('tests', 'test_projects', 'import_example', 'python', 'library.py')
    executable_source_path = os.path.join('tests', 'test_projects', 'import_example', 'python', 'useLibrary.py')
    # Run the program that includes the import.
    result = subprocess.run(['python3', executable_source_path], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
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
    subprocess.run(['go', 'mod', 'init', 'library'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Run the program that includes the import.
    result = subprocess.run(['go', 'run', os.path.join('useLibrary', 'main.go')], check=True, capture_output=True)
    self.assertEqual(b'Hello from the library\n', result.stdout)
    # Cleanup compiled files.
    subprocess.run(['rm', 'go.mod'], check=True)
    subprocess.run(['rm', 'library.go'], check=True)
    subprocess.run(['rm', os.path.join('useLibrary', 'main.go')], check=True)
    os.chdir(os.path.join('..', '..', '..', '..'))


if __name__ == '__main__':
  unittest.main()

