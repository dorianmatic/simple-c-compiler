import fileinput
import pickle
import sys
from pathlib import Path

sys.path.append('..')
from lab2.utils.LRParser import LRParser

class SyntaxAnalyzer:
    def __init__(self, actions, new_states, sequence, sync_terminals):
        self.parser = LRParser(actions, new_states, sequence)
        self.sync_terminals = sync_terminals

    def analyze(self):
        while not self.parser.parse():
            # parser failed - perform error recovery
            sequence = self.parser.get_sequence()
            for seq_element, i in enumerate(sequence):
                if seq_element[0] in self.sync_terminals:
                    sequence = sequence[i:]

            self.parser.set_sequence(sequence)

        return self.parser.get_tree()


if __name__ == '__main__':
    # Load the data that was serialized by the SLA and re-build the parser
    data = pickle.load(Path(__file__).parent.joinpath('SA_data.pkl').open('rb'))

    sequence = []
    for line in fileinput.input():
        sequence.append(line)
    # print(data)
    sa = SyntaxAnalyzer(data['parser_actions'], data['parser_new_states'], sequence, data['sync_non_terminals'])
    print(sa.analyze())