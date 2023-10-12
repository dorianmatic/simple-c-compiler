import sys
from pathlib import Path

sys.path.append('..')

import pickle
from lab1.utils.ENFA import ENFA


class LexicalAnalyzer:
    def __init__(self, rules, source, init_state):
        self.rules = rules
        self.source = source

        self.state = init_state
        self.line_n = 1

    def analyze(self):
        cursor = 0
        while cursor != len(source):
            prefix_with_applicable_rule = 0
            ran = 1
            while cursor + ran <= len(source):
                if self._first_applicable_rule(self.source[cursor:cursor + ran]):
                    prefix_with_applicable_rule = ran
                ran += 1
            ran -= 1

            # Perform error recovery
            if prefix_with_applicable_rule == 0:
                cursor += 1
                continue

            rule = self._first_applicable_rule(self.source[cursor:cursor + prefix_with_applicable_rule])
            lex_unit, offset = self._apply_rule(rule)

            if lex_unit != '-':
                yield lex_unit, self.line_n, self.source[cursor:cursor + (offset or prefix_with_applicable_rule)]
            cursor += offset or prefix_with_applicable_rule

    def _apply_rule(self, rule):
        offset = 0
        for action in rule['actions'][1:]:
            if action.startswith('NOVI_REDAK'):
                self.line_n += 1
            elif action.startswith('UDJI_U_STANJE'):
                self.state = action.split(' ')[1]
            elif action.startswith('VRATI_SE'):
                offset = int(action.split(' ')[1])

        return rule['actions'][0], offset

    def _first_applicable_rule(self, source_segment):
        # print('########', repr(source_segment))
        i = 0

        for rule in filter(lambda rule: rule['state'] == self.state, self.rules):
            # print(f"--{i} {repr(rule['regex'])} {rule['actions']}")
            if rule['nfa'].validate(source_segment):
                return rule
            i += 1

        return None


if __name__ == '__main__':
    data = pickle.load(Path(__file__).parent.joinpath('LA_data.pkl').open('rb'))
    rules = list(map(lambda rule: rule | {'nfa': ENFA(definition=rule['nfa_definition'])}, data['rules']))

    source = sys.stdin.read()
    la = LexicalAnalyzer(rules, source, data['init_state'])
    for out in la.analyze():
        print(*out)
