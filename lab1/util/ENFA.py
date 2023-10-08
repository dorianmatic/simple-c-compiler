from collections import defaultdict
from regex import split_by_or
import copy


class ENFA:
    table = {}
    active_states = []
    acceptable_states = []

    def __init__(self, **kwargs):
        if regex := kwargs.get('regex', None):
            left_state, right_state = self._init_from_regex(regex)
            self.active_states.append(left_state)
            self.acceptable_states.append(right_state)

        if table := kwargs.get('definition', None):
            self._init_from_definition(table)

    def _add_state(self):
        n_states = len(self.table.items())
        self.table[n_states] = defaultdict(list)

        return n_states

    def _add_transition(self, source, target, trigger=None):
        if trigger is not None:
            self.table[source][trigger].append(target)
        else:
            self.table[source]['eps'].append(target)

    def _init_from_regex(self, regex):
        or_choices = split_by_or(regex)

        left_state = self._add_state()
        right_state = self._add_state()

        if len(or_choices) != 0:
            for choice in or_choices:
                tmp_left, tmp_right = self.init_from_regex(choice)

                self._add_transition(left_state, tmp_left)
                self._add_transition(tmp_right, right_state)
        else:
            prefixed = False
            last_state = left_state

            for i, c in enumerate(regex):
                state_a, state_b = None, None
                if prefixed:
                    pass
                else:
                    if c == '\\':
                        prefixed = True
                        continue
                    if c != '(':
                        state_a = self._add_state()
                        state_b = self._add_state()

                        if c == '$':
                            self._add_transition(state_a, state_b)
                        else:
                            self._add_transition(state_a, state_b, c)
                    else:
                        closing_parent = regex[i:].index(')')
                        state_a, state_b = self.init_from_regex(regex[i+1:closing_parent-1])

                        i = closing_parent

                if i + 1 < len(regex) and regex[i+1] == '*':
                    state_x = state_a
                    state_y = state_b

                    state_a = self._add_state()
                    state_b = self._add_state()

                    self._add_transition(state_a, state_x)
                    self._add_transition(state_y, state_b)
                    self._add_transition(state_a, state_b)
                    self._add_transition(state_y, state_x)
                    i += 1

                self._add_transition(last_state, state_a)
                last_state = state_b

            self._add_transition(last_state, right_state)
            return left_state, right_state

    def _init_from_definition(self, definition):
        self.table = definition['table']
        self.active_states = definition['active_states']
        self.acceptable_states = definition['active_states']

    def export_definition(self):
        return {
            'table': copy.deepcopy(self.table),
            'active_states': self.active_states.copy(),
            'acceptable_states': self.acceptable_states.copy()
        }
