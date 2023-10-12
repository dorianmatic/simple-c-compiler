import argparse
import subprocess
from pathlib import Path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def test_case_directories(top_level_path):
    for path in top_level_path.iterdir():
        if path.is_dir():
            yield path


def print_process_result(result):
    if result.returncode == 0:
        print(f"{bcolors.OKGREEN}OK{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAIL")
        print(f"{result.stderr}{bcolors.ENDC}")


parser = argparse.ArgumentParser()
parser.add_argument('--examples', help='Test examples top level folder path')
parser.add_argument('--generator', help='Lexical Analyzer Generator script path')
parser.add_argument('--analyzer', help='Lexical Analyzer script path')

args = parser.parse_args()

examples_path = args.examples or Path(__file__).parents[2].joinpath('examples/lab1_teza')
generator_script = args.generator or Path(__file__).parents[2].joinpath('GLA.py')
lex_analyzer_script = args.analyzer or Path(__file__).parents[2].joinpath('analizator/LA.py')

total = 0
passed = 0

for test_case_path in test_case_directories(examples_path):
    total += 1

    print(f"{bcolors.OKBLUE}============== Test Case: {test_case_path}{bcolors.ENDC}")
    lang_definition_path = test_case_path.joinpath('test.lan')
    la_input_path = test_case_path.joinpath('test.in')
    la_output_path = test_case_path.joinpath('test.out')

    print(f"Running generator... ", end='')
    generator_result = subprocess.run(['python', generator_script], text=True, capture_output=True,
                                      stdin=lang_definition_path.open())
    print_process_result(generator_result)

    print(f"Running analyzer... ", end='')
    lex_analyzer_result = subprocess.run(['python', lex_analyzer_script], text=True, capture_output=True,
                                         stdin=la_input_path.open())
    print_process_result(generator_result)

    expected = ''.join(la_output_path.open().readlines())
    if expected == lex_analyzer_result.stdout:
        print(f"{bcolors.OKGREEN}Passed.{bcolors.ENDC}")
        passed += 1
    else:
        print(f"{bcolors.FAIL}Failed.{bcolors.ENDC}")


print(f"{bcolors.OKBLUE}==== Passed: {passed}/{total} ===={bcolors.ENDC}")