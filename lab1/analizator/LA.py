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
            ran = 1
            while self._first_applicable_rule(self.source[cursor:cursor + ran]) and cursor + ran <= len(source):
                ran += 1

            ran -= 1

            # Perform error recovery
            if ran == 0:
                cursor += 1
                continue

            rule = self._first_applicable_rule(self.source[cursor:cursor + ran])
            lex_unit, offset = self._apply_rule(rule)

            yield lex_unit, self.line_n, self.source[cursor:cursor + (offset or ran)]
            cursor += offset or ran

    def _apply_rule(self, rule):
        offset = 0
        for action in rule['actions'][1:]:
            if action.startswith('NOVI_REDAK'):
                self.line_n += 1
            elif action.startswith('UDJI_U_STANJE'):
                self.state = action.split(' ')[1]
            elif action.startswith('VRATI_SE'):
                self.offset = int(action.split(' ')[1])

        return rule['actions'][0], offset

    def _first_applicable_rule(self, source_segment):
        for rule in self.rules:
            if rule['state'] == self.state and rule['nfa'].validate(source_segment):
                return rule

        return None


if __name__ == '__main__':
    data = pickle.load(Path(__file__).parent.joinpath('LA_data.pkl').open('rb'))
    rules = list(map(lambda rule: rule | {'nfa': ENFA(definition=rule['nfa_definition'])}, data['rules']))

    source = ""
    try:
        while source_line := input():
            source += source_line
    except EOFError:
        pass

    la = LexicalAnalyzer(rules, source, data['init_state'])
    for out in la.analyze():
        print(*out)
