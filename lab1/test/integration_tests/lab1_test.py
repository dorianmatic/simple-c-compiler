import argparse
import subprocess
import time
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


def print_process_result(result, time_elapsed):
    if result.returncode == 0:
        print(f"{bcolors.OKGREEN}OK{bcolors.ENDC}", end=' ')
    else:
        print(f"{bcolors.FAIL}FAIL", end=' ')

    print(f"{bcolors.OKCYAN}[{time_elapsed}s]{bcolors.ENDC}")


def run(script, input_path):
    start_time = time.time()
    result = subprocess.run(['python', script], text=True, capture_output=True, stdin=input_path.open())
    print_process_result(result, time.time() - start_time)

    return result


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

begin_time = time.time()
for test_case_path in test_case_directories(examples_path):
    total += 1

    print(f"{bcolors.OKBLUE}============== Test Case: {test_case_path}{bcolors.ENDC}")
    lang_definition_path = test_case_path.joinpath('test.lan')
    la_input_path = test_case_path.joinpath('test.in')
    la_output_path = test_case_path.joinpath('test.out')

    print(f"Running generator... ", end='')
    run(generator_script, lang_definition_path)

    print(f"Running analyzer... ", end='')
    lex_analyzer_result = run(lex_analyzer_script, la_input_path)

    expected = ''.join(la_output_path.open().readlines())
    if expected == lex_analyzer_result.stdout:
        print(f"{bcolors.OKGREEN}Passed.{bcolors.ENDC}")
        passed += 1
    else:
        print(f"{bcolors.FAIL}Failed.{bcolors.ENDC}")


print(f"{bcolors.OKBLUE}============================{bcolors.ENDC}")
print(f"Passed: {passed}/{total}")
print(f"Time elapsed: {time.time() - begin_time}s")
