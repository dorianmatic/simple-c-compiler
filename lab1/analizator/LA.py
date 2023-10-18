import sys
import pickle
from pathlib import Path

# A hack needed to import from the parent folder
sys.path.append('..')
from lab1.utils.ENFA import ENFA


class LexicalAnalyzer:
    def __init__(self, rules, source, init_state):
        self.rules = rules
        self.source = source

        self.state = init_state
        self.line_n = 1

    def analyze(self):
        """ Yields to caller lexical units from the source code.

        Finds lexical units by using Longest prefix matching rule:
        1. Start by getting all the rules for the current state.
        2. Refine that list by reading source symbols one by one, until no rules are applicable.
        3. Apply the first rule for the longest prefix that had an applicable rule. If there is none, perform error recovery.
        4. Yield the lexical unit, line number and source segment.
        5. Repeat until the end on source code.

        """

        cursor = 0
        while cursor != len(source):
            # Find the longest prefix that has an applicable rule. For each step, keep list of possible rules.
            prefix_with_applicable_rule = 0
            active_rules = self._get_active_rules_for_state()
            ran = 1
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

    @staticmethod
    def _refine_active_rules(active_rules, source_segment):
        """
         Refine the list of currently active rules by keeping only the ones that return 'potential' or 'match' when
         evaluated on the source segment.
        """

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
    # Load date that was serialized by GLA and re-build the automata
    data = pickle.load(Path(__file__).parent.joinpath('LA_data.pkl').open('rb'))
    rules = list(map(lambda rule: rule | {'nfa': ENFA(definition=rule['nfa_definition'])}, data['rules']))

    source = ''
    for line in sys.stdin:
        source += line

    la = LexicalAnalyzer(rules, source, data['init_state'])
    for out in la.analyze():
        print(*out)
