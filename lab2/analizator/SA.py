import fileinput
import pickle
import sys
from pathlib import Path

sys.path.append('..')


class SyntaxAnalyzer:
    def __init__(self):
        pass
    def analyze(self):
        pass


if __name__ == '__main__':
    data = pickle.load(Path(__file__).parent.joinpath('LA_data.pkl').open('rb'))


    for line in fileinput.input():
        pass