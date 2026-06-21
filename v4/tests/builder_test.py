import unittest
import builder
import os
import subprocess

class TestBuilder(unittest.TestCase):
  """Exercises the builder for all languages."""

  def test_build_and_execute_hello_world_in_c(self):
    builder.convert_project(os.path.join('tests', 'test_projects', 'hello_world'), 'c')
    compilation_directory = os.path.join('tests', 'test_projects', 'hello_world', 'c')
    # Compile the main function.
    binary_source_path = os.path.join(compilation_directory, 'headspace', 'tests', 'hello.c')
    executable_path = os.path.join(compilation_directory, 'headspace', 'tests', 'hello')
    result = subprocess.run(['gcc', '-Wall', '-Wextra', '-std=c89', '-pedantic',
                             '-Wmissing-prototypes', '-Wstrict-prototypes',
                             '-Wold-style-definition', '-o',
                             executable_path, binary_source_path], check=True, capture_output=True)
    # Run the compiled program.
    result = subprocess.run([executable_path], check=True, capture_output=True)
    subprocess.run(['rm', executable_path], check=True)
    self.assertEqual(b'hello\n', result.stdout)

  def test_build_and_execute_hello_world_in_python(self):
    builder.convert_project(os.path.join('tests', 'test_projects', 'hello_world'), 'py')
    compilation_directory = os.path.join('tests', 'test_projects', 'hello_world', 'py')
    executable_source_path = os.path.join(compilation_directory, 'headspace', 'tests', 'hello.py')
    test_env = os.environ.copy()
    test_env['PYTHONPATH'] = compilation_directory
    # Run the program.
    result = subprocess.run(['python3', executable_source_path], env=test_env, check=True, capture_output=True)
    self.assertEqual(b'hello\n', result.stdout)

  def test_build_and_execute_hello_world_in_go(self):
    builder.convert_project(os.path.join('tests', 'test_projects', 'hello_world'), 'go')
    compilation_directory = os.path.join('tests', 'test_projects', 'hello_world', 'go')
    executable_source_path = os.path.join('tests', 'test_projects', 'import_example', 'go', 'hello', 'main.go')
    # Generate the go module.
    os.chdir(compilation_directory)
    subprocess.run(['go', 'mod', 'init', 'hello'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Run the program that includes the import.
    result = subprocess.run(['go', 'run', os.path.join('hello', 'main.go')], check=True, capture_output=True)
    # Cleanup compiled files.
    os.chdir(os.path.join('..', '..', '..', '..'))
    self.assertEqual(b'hello\n', result.stdout)


if __name__ == '__main__':
  unittest.main()

