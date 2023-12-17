import argparse
import subprocess
from subprocess import TimeoutExpired
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
    for path in sorted(top_level_path.iterdir()):
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
    try:
        result = subprocess.run(['python', script], text=True, capture_output=True,
                                stdin=input_path.open(), timeout=250)
        print_process_result(result, time.time() - start_time)

        return result
    except TimeoutExpired:
        print(f"{bcolors.FAIL} TIMEOUT {bcolors.ENDC}")

        return None


parser = argparse.ArgumentParser()
parser.add_argument('--examples', help='Test examples top level folder path')
parser.add_argument('--analyzer', help='Semantic Analyzer script path')

args = parser.parse_args()
examples_path = args.examples or Path(__file__).parents[2].joinpath('examples/lab3_teza')
semantic_analyzer_script = args.analyzer or Path(__file__).parents[2].joinpath('SemantickiAnalizator.py')

total = 0
passed = 0

begin_time = time.time()
for test_case_path in test_case_directories(examples_path):
    total += 1

    print(f"{bcolors.OKBLUE}============== Test Case: {test_case_path}{bcolors.ENDC}")
    sa_input_path = test_case_path.joinpath('test.in')
    sa_output_path = test_case_path.joinpath('test.out')

    print(f"Running analyzer... ", end='')
    semantic_analyzer_result = run(semantic_analyzer_script, sa_input_path)
    if semantic_analyzer_result is None:
        continue

    expected = ''.join(sa_output_path.open().readlines())
    if expected == semantic_analyzer_result.stdout:
        print(f"{bcolors.OKGREEN}Passed.{bcolors.ENDC}")
        passed += 1
    else:
        print(f"{bcolors.FAIL}Failed.{bcolors.ENDC}")


print(f"{bcolors.OKBLUE}============================{bcolors.ENDC}")
print(f"Passed: {passed}/{total}")
print(f"Time elapsed: {time.time() - begin_time}s")
