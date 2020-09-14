import pytest
import pycodestyle
import os
import re

def get_tests(filename):
    '''
    Gets a tests array from the docstring meta tag
    for a source file
    '''

    tests = []

    file = open(filename, 'r')

    for line in file:
        if line.startswith('__tests__'):
            tests_string = re.findall(r'\[(.*)\]', line)
            tests = re.findall('["\']?([^"\']+)["\']?', tests_string[0])
            break

    file.close()

    return tests

def get_files_for_test(test, base_dir='.'):
    files_to_test = []

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                if test in get_tests(os.path.join(root, file)):
                    files_to_test.append(os.path.join(root, file))

    return files_to_test

@pytest.mark.parametrize('file_path', get_files_for_test(test='pep8'))
def test_pep8(file_path):
    fchecker = pycodestyle.Checker(file_path, show_source=True)
    file_errors = fchecker.check_all()
    assert file_errors == 0
