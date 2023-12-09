from collections import defaultdict
from lab2.utils.StartSet import *


class ENFA:
    """Non-deterministic finite state automaton with (or without) epsilon-transitions."""

    def __init__(self, transitions, state_enumeration, terminals, non_terminals):
        self.transitions = transitions
        self.state_enumeration = state_enumeration

        self.terminals = terminals
        self.non_terminals = non_terminals
        self.epsilon_closures = self._get_epsilon_closures()

    @classmethod
    def from_context_free_grammar(cls, productions, terminals, non_terminals):
        """
        Construct an epsilon non-deterministic finite automaton (ENFA) from a given context-free grammar.

        Parameters:
        - productions (list): A list of production rules of the context-free grammar.
        - terminals (list): A set of terminal symbols.
        - non_terminals (list): A set of non-terminal symbols.

        Returns:
        - ENFA: An instance of the ENFA class constructed from the given context-free grammar.
        """

        states = cls._get_states(productions)
        start_utils = StartsUtils(productions, terminals, non_terminals)
        transitions, state_enumeration = cls._construct_ENFA_transitions(states, start_utils)

        return cls(transitions, state_enumeration, terminals, non_terminals)

    @classmethod
    def _get_states(cls, productions):
        """
        Based on grammar productions, create a list of states for the automaton.

        Parameters:
        - productions (list): A list of production rules of the context-free grammar.

        Returns:
        - states (list): A list of possible ENFA states.
        """

        states = []
        for production in productions:
            left = production["left"]
            right = production["right"]
            if right == ["$"]:
                right = []
            right_lr = list(right)
            for i in range(len(right) + 1):
                right_lr.insert(i, 0)
                state = {"left": left, "right": right_lr}
                states.append(state)
                right_lr = list(right)

        return states

    @classmethod
    def _find_terminals(cls, sequence, current_state, start_utils):
        """
        Return the list of all possible terminals that beta can start with.

        Parameters:
        - beta (list): A sequence of terminal and non-terminal symbols.
        - current_state: Current ENFA state.
        - start_utils (StartUtils): A utility object for START sets.

        Returns:
        - terminals (list): List of terminals sequence could start with.
        """

        if sequence:
            terminals = start_utils.starts_set_for_sequence(sequence)
            if start_utils.generate_empty(sequence):
                terminals = terminals + list(current_state["terminals"])
        else:
            terminals = current_state["terminals"]

        return terminals

    @classmethod
    def _construct_ENFA_transitions(cls, states, start_utils):
        """
        Constructs transitions for an ε-NFA (Nondeterministic Finite Automaton) using
        the given states and start utilities.

        Parameters:
        - states: a list of dictionaries representing the production states of the ε-NFA.
        - start_utils: an instance of the StartSet class for finding start symbols.

        Returns:
        - transitions: a defaultdict(list) representing the transitions of the ε-NFA.
        - state_enumeration: a list of enumerated states in the ε-NFA.
        """

        state_0 = {"production": states[0], "terminals": "!"}
        transitions = defaultdict(list)
        queue = [state_0]
        visited = [state_0]
        state_enumeration = [state_0]

        while queue:
            current_state = queue.pop(0)
            current_state_number = state_enumeration.index(current_state)
            right_current_state = current_state["production"]["right"]
            parser_read_point = right_current_state.index(0)

            if parser_read_point + 1 < len(right_current_state):
                inp = right_current_state[parser_read_point + 1]
                delta = (current_state_number, inp)
                new_right_state = list(right_current_state)
                new_right_state.remove(0)
                new_right_state.insert(parser_read_point + 1, 0)
                input_transition_state = {
                    "left": current_state["production"]["left"],
                    "right": new_right_state,
                }
                new_state = {
                    "production": input_transition_state,
                    "terminals": current_state["terminals"],
                }

                if new_state in state_enumeration:
                    new_state_number = state_enumeration.index(new_state)
                else:
                    state_enumeration.append(new_state)
                    new_state_number = len(state_enumeration) - 1

                if new_state not in visited:
                    visited.append(new_state)
                    queue.append(new_state)
                transitions[delta].append(new_state_number)

                epsilon_transition_states = [state for state in states if
                                             state["left"] == inp and state["right"][0] == 0]
                for state in epsilon_transition_states:
                    delta = (current_state_number, "$")
                    terminals = cls._find_terminals(right_current_state[parser_read_point + 2:], current_state,
                                                    start_utils)

                    new_state = {"production": state, "terminals": terminals}
                    if new_state in state_enumeration:
                        new_state_number = state_enumeration.index(new_state)
                    else:
                        state_enumeration.append(new_state)
                        new_state_number = len(state_enumeration) - 1

                    if new_state not in visited:
                        visited.append(new_state)
                        queue.append(new_state)
                    transitions[delta].append(new_state_number)

        return transitions, state_enumeration

    def _epsilon_closure(self, start_state_number):
        """
        Return the epsilon closure of a given start state number.

        Parameters:
        start_state_number (int): The start state number.

        Returns:
        frozenset: The epsilon closure set.

        """
        closure = {start_state_number}
        queue = {start_state_number}
        visited = set()

        while queue:
            state_number = queue.pop()
            for episilon_state in self.transitions[(state_number, '$')]:
                closure.add(episilon_state)

                if episilon_state not in visited:
                    queue.add(episilon_state)
            visited.add(state_number)

        return frozenset(closure)

    def _get_epsilon_closures(self):
        """
        Return the list of epsilon closures for every state.

        :return: epsilon_closures: list of closures for every state.
        """

        epsilon_closures = []
        for state_number in range(len(self.state_enumeration)):
            epsilon = self._epsilon_closure(state_number)

            epsilon_closures.append({'state': state_number, 'epsilon': epsilon})

        return epsilon_closures
