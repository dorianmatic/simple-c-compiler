from collections import defaultdict
from .regex import split_by_or
from .misc import find_closing_parent
import copy


class ENFA:
    """Non-deterministic finite state automata with epsilon-transitions."""

    def __init__(self, **kwargs):
        self.table = {}
        self.active_states = []
        self.acceptable_states = []
        self.original_active = None

        if regex := kwargs.get('regex', None):
            left_state, right_state = self._init_from_regex(regex)

            self.original_active = left_state
            self.acceptable_states.append(right_state)

            self._reset_automata()
        if table := kwargs.get('definition', None):
            self._init_from_definition(table)

    def export_definition(self):
        """Export the automata definition (for serialization)."""

        return {
            'table': copy.deepcopy(self.table),
            'acceptable_states': self.acceptable_states.copy(),
            'original_active': self.original_active
        }

    def validate(self, string):
        """ Validates a string using the automata.

            Returns one of three values:
            1. 'match' - after validation there is an active state that is also acceptable
            2. 'potential' - after validation there are some states, none are acceptable. If more symbols are read,
            this NFA could move into an acceptable state.
            3. 'no-match' - there are no active states. It's impossible for this NFA to move into an acceptable state.

        """

        self._reset_automata()

        for c in string:
            self._step(c)

        active_acceptable_states = set(self.active_states).intersection(set(self.acceptable_states))
        if len(active_acceptable_states) != 0:
            return 'match'
        elif len(self.active_states) != 0:
            return 'potential'
        else:
            return 'no-match'

    def _add_state(self):
        n_states = len(self.table.items())
        self.table[n_states] = defaultdict(list)

        return n_states

    def _add_transition(self, source, target, trigger=None):
        """Add a transition to the automata, if the trigger is None, transition is an epsilon transition."""

        if trigger is not None:
            self.table[source][trigger].append(target)
        else:
            self.table[source]['eps'].append(target)

    def _init_from_regex(self, regex):
        """Initialize the automata from a regex in a recursive way. Algorithm provided."""

        or_choices = split_by_or(regex)

        left_state = self._add_state()
        right_state = self._add_state()

        if len(or_choices) != 0:
            for choice in or_choices:
                tmp_left, tmp_right = self._init_from_regex(choice)

                self._add_transition(left_state, tmp_left)
                self._add_transition(tmp_right, right_state)
        else:
            prefixed = False
            last_state = left_state

            i = 0
            while i < len(regex):
                if prefixed:
                    prefixed = False
                    if regex[i] == 't':
                        trigger = '\t'
                    elif regex[i] == 'n':
                        trigger = '\n'
                    elif regex[i] == '_':
                        trigger = ' '
                    else:
                        trigger = regex[i]

                    state_a = self._add_state()
                    state_b = self._add_state()
                    self._add_transition(state_a, state_b, trigger)
                else:
                    if regex[i] == '\\':
                        prefixed = True
                        i += 1
                        continue
                    if regex[i] != '(':
                        state_a = self._add_state()
                        state_b = self._add_state()

                        if regex[i] == '$':
                            self._add_transition(state_a, state_b)
                        else:
                            self._add_transition(state_a, state_b, regex[i])
                    else:
                        closing_parent = find_closing_parent(regex[i:])
                        state_a, state_b = self._init_from_regex(regex[i + 1:i + closing_parent])
                        i += closing_parent

                if i + 1 < len(regex) and regex[i + 1] == '*':
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
                i += 1

            self._add_transition(last_state, right_state)
        return left_state, right_state

    def _init_from_definition(self, definition):
        """Load the automata from a definition dictionary. """

        self.table = definition['table']
        self.acceptable_states = definition['acceptable_states']
        self.original_active = definition['original_active']

    def _reset_automata(self):
        """Reset the automata to the initial state."""

        self.active_states = self._activate_state(self.original_active)

    def _activate_state(self, state):
        """Activate the state and all of its epsilon transitions."""

        to_activate = [state]
        new_active_states = []

        while len(to_activate) != 0:
            s = to_activate[0]

            if s not in new_active_states:
                new_active_states.append(s)

            to_activate.extend(self.table[s]['eps'])
            to_activate = list(set(to_activate[1:]))

        return new_active_states

    def _step(self, symbol):
        """"Perform an automata step (read a symbol)."""

        new_active = []
        for state in self.active_states:
            for new_state in self.table[state][symbol]:
                new_active.extend(self._activate_state(new_state))

        self.active_states = new_active
