# The builder takes a headspace source directory and converts it to the target
# language. It can also run a target module in a directory. The expected
# structure for the project directory is that it will contain a headspace
# directory with source files. The project converter will create language-
# specific peer directories.

import sys
import os
import pathlib
import parser
import converter


SUPPORTED_LANGUAGES = ['c', 'python', 'go', 'javascript', 'java', 'dotnet']


def convert_project(project_directory, target_language):
  if target_language == 'all':
    for supported_language in SUPPORTED_LANGUAGES:
      convert_project(project_directory, supported_language)
    return

  directories = [f for f in pathlib.Path(project_directory).iterdir() if f.is_dir()]
  print('converting project:', project_directory)
  print('to target language:', target_language)

  # The source code must be found in a project's headspace directory.
  headspace_directory = None
  target_directory = None
  for sub_directory in directories:
    if 'headspace' in sub_directory.parts[-1]:
      headspace_directory = sub_directory
    elif target_language == sub_directory.parts[-1]:
      target_directory = sub_directory
  if not headspace_directory:
    print('The project directory did not contain a headspace source directory')
    sys.exit(1)

  # If the output directory for the language is missing, create it.
  if not target_directory:
    pathlib.Path(os.path.join(project_directory, target_language)).mkdir()
    directories = [f for f in pathlib.Path(project_directory).iterdir() if f.is_dir()]
    for sub_directory in directories:
      if target_language in sub_directory.parts[-1]:
        target_directory = sub_directory

  # TODO: handle subdirectories in the source code.
  for source_location in headspace_directory.iterdir():
    if source_location.is_file():
      with open(source_location, 'r') as source_file:
        tree = parser.parse_source(source_file.read())
        results_files = converter.convert(tree, target_language)
        # Write out the results files to the output directory.
        for result_file in results_files:
          # Create the filename's directory if it doesn't exist.
          result_path = pathlib.Path(os.path.join(target_directory, result_file.filename))
          result_path.parent.mkdir(parents=True, exist_ok=True)
          result_path.write_text(result_file.content)


if __name__ == '__main__':
  if len(sys.argv) < 3:
    print('To convert a project, the project source folder and target language must be specified')
    sys.exit(1)
  convert_project(sys.argv[1], sys.argv[2])
