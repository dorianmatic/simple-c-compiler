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
        """Perform lexical analysis on the source."""

        cursor = 0
        while cursor != len(source):
            prefix_with_applicable_rule = 0

            # Find the longest prefix that has an applicable rule, start from the end of source code
            ran = 1
            active_rules = self._get_active_rules_for_state()
            applicable_rule = None
            while cursor + ran < len(source):
                new_active_rules, new_applicable_rule = self._refine_active_rules(active_rules,
                                                                                  source[cursor:cursor + ran])
                if len(new_active_rules) != 0:
                    active_rules = new_active_rules
                else:
                    break

                if new_applicable_rule:
                    applicable_rule = new_applicable_rule
                    prefix_with_applicable_rule = ran

                ran += 1

            # If there is no prefix with an applicable rule, perform error recovery by ignoring the first symbol
            if prefix_with_applicable_rule == 0:
                cursor += 1
                continue

            lex_unit, offset = self._apply_rule(applicable_rule)

            # Don't yield if the lexical unit is '-', that unit should be discarded (e.g. whitespace)
            if lex_unit != '-':
                yield lex_unit, self.line_n, self.source[cursor:cursor + (offset or prefix_with_applicable_rule)]
            cursor += offset or prefix_with_applicable_rule

    def _apply_rule(self, rule):
        """Apply provided analyzer rule."""

        offset = 0
        for action in rule['actions'][1:]:
            if action.startswith('NOVI_REDAK'):
                self.line_n += 1
            elif action.startswith('UDJI_U_STANJE'):
                self.state = action.split(' ')[1]
            elif action.startswith('VRATI_SE'):
                offset = int(action.split(' ')[1])

        return rule['actions'][0], offset

    def _refine_active_rules(self, active_rules, source_segment):
        """Find the first applicable rule for a given source segment taking into account the current analyzer state."""

        new_active_rules = []
        first_applicable = None
        for rule in active_rules:
            validation_result = rule['nfa'].validate(source_segment)

            if validation_result == 'match' and first_applicable is None:
                first_applicable = rule

            if validation_result != 'no-match':
                new_active_rules.append(rule)

        return new_active_rules, first_applicable

    def _get_active_rules_for_state(self):
        return list(filter(lambda rule: rule['state'] == self.state, self.rules))


if __name__ == '__main__':
    data = pickle.load(Path(__file__).parent.joinpath('LA_data.pkl').open('rb'))
    rules = list(map(lambda rule: rule | {'nfa': ENFA(definition=rule['nfa_definition'])}, data['rules']))

    source = ''
    for line in sys.stdin:
        source += line

    la = LexicalAnalyzer(rules, source, data['init_state'])
    for out in la.analyze():
        print(*out)
