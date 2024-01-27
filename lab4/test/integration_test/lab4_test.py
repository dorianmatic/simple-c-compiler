import argparse
import os.path
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


def run_python(script, input_path):
    start_time = time.time()
    try:
        result = subprocess.run(['python', script], text=True, capture_output=True,
                                stdin=input_path.open(), timeout=250)
        print_process_result(result, time.time() - start_time)

        return result
    except TimeoutExpired:
        print(f"{bcolors.FAIL} TIMEOUT {bcolors.ENDC}")

        return None


def run_javascript(script, input_path):
    start_time = time.time()
    try:
        result = subprocess.run(['node', script, input_path], text=True, capture_output=True, timeout=5)
        print_process_result(result, time.time() - start_time)

        return result
    except TimeoutExpired:
        print(f"{bcolors.FAIL} TIMEOUT {bcolors.ENDC}")

        return None

parser = argparse.ArgumentParser()
parser.add_argument('--examples', help='Test examples top level folder path')
parser.add_argument('--generator', help='Code generator script path')
parser.add_argument('--simulator', help='Processor simulator script path')

args = parser.parse_args()
examples_path = Path(args.examples) if args.examples else Path(__file__).parents[2].joinpath('examples/lab4_teza')
code_generator_script = Path(args.generator) if args.generator else Path(__file__).parents[2].joinpath('GeneratorKoda.py')
simulator_script = Path(args.simulator) if args.simulator else Path(__file__).parents[2].joinpath('sim/main.js')
generator_result_path = Path(__file__).parents[2].joinpath('a.frisc')

total = 0
passed = 0

begin_time = time.time()
for test_case_path in test_case_directories(examples_path):
    total += 1

    print(f"{bcolors.OKBLUE}============== Test Case: {test_case_path}{bcolors.ENDC}")
    gen_input_path = test_case_path.joinpath('test.in')
    sim_output_path = test_case_path.joinpath('test.out')

    print(f"Running code generator... ", end='')
    run_python(code_generator_script, gen_input_path)

    print(f"Running simulator... ", end='')
    simulator_result = run_javascript(simulator_script, generator_result_path)
    expected = ''.join(sim_output_path.open().readlines())

    if simulator_result and expected.strip() == simulator_result.stdout.strip():
        print(f"{bcolors.OKGREEN}Passed.{bcolors.ENDC}")
        passed += 1
    else:
        print(f"{bcolors.FAIL}Failed.{bcolors.ENDC}")

    if os.path.exists(generator_result_path):
        os.remove(generator_result_path)


print(f"{bcolors.OKBLUE}============================{bcolors.ENDC}")
print(f"Passed: {passed}/{total}")
print(f"Time elapsed: {time.time() - begin_time}s")
