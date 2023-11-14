import time
from functools import cache
from lab2.utils.StartSet import *


class ENFA:
    """Non-deterministic finite state automata with (or without) epsilon-transitions."""

    def __init__(self, transitions, state_enumeration, terminals, non_terminals):
        self.transitions = transitions
        self.state_enumeration = state_enumeration

        self.terminals = terminals
        self.non_terminals = non_terminals
        # t = time.time()
        self.epsilon_closures = self.get_epsilon_closures()
        # print(f" get_epsilon_list -> {time.time() - t}")

    @classmethod
    def from_context_free_grammar(cls, productions, terminals, non_terminals):
        """
        Build ENFA from context-free grammar.

        :param productions: Grammar productions.
        :param terminals: Grammar terminal symbols.
        :param non_terminals: Grammar non-terminal symbols
        :return: ENFA
        """
        states = cls.get_states(productions)
        # t = time.time()
        start_utils = Zapocinje(productions, terminals, non_terminals)
        # print(f" Zapocinje -> {time.time() - t}")

        # t = time.time()
        transitions, state_enumeration = cls.construct_enka_transitions(states, start_utils)
        # print(f" construct_enka_transitions -> {time.time() - t}")

        return cls(transitions, state_enumeration, terminals, non_terminals)

    @classmethod
    def get_states(cls, productions):
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
    def find_terminals(cls, beta, current_state, start_utils):
        if beta:
            terminals = start_utils.starts_set_for_sequence(beta)
            if start_utils.generate_empty(beta):
                terminals = terminals + list(current_state["terminals"])
        else:
            terminals = current_state["terminals"]

        return terminals

    @classmethod
    def bfs_check(cls, visited, queue, transitions, transition, new_state):
        if new_state not in visited:
            visited.append(new_state)
            queue.append(new_state)
        transitions.append(transition)

        return transitions, queue, visited

    @classmethod
    def construct_enka_transitions(cls, states, start_utils):
        state_0 = {"production": states[0], "terminals": "!"}
        transitions = []
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
                delta = [current_state_number, inp]
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

                transition = {
                    "delta": delta,
                    "state": new_state_number,
                }

                transitions, queue, visited = cls.bfs_check(
                    visited, queue, transitions, transition, new_state
                )

                epsilon_transition_states = [
                    state
                    for state in states
                    if state["left"] == inp and state["right"][0] == 0
                ]

                for state in epsilon_transition_states:
                    delta = [current_state_number, "$"]
                    terminals = cls.find_terminals(right_current_state[parser_read_point + 2:], current_state,
                                                   start_utils)

                    new_state = {"production": state, "terminals": terminals}

                    if new_state in state_enumeration:
                        new_state_number = state_enumeration.index(new_state)
                    else:
                        state_enumeration.append(new_state)
                        new_state_number = len(state_enumeration) - 1

                    transition = {
                        "delta": delta,
                        "state": new_state_number,
                    }
                    transitions, queue, visited = cls.bfs_check(
                        visited, queue, transitions, transition, new_state
                    )

        return transitions, state_enumeration

    @cache
    def find_transitions(self, state_number, symbol):
        return list(filter(lambda x: x['delta'] == [state_number, symbol], self.transitions))

    def epsilon_closure(self, start_state_number):
        closure = {start_state_number}
        queue = {start_state_number}
        visited = set()

        while queue:
            state_number = queue.pop()
            for episilon_transition in self.find_transitions(state_number, '$'):
                closure.add(episilon_transition['state'])

                if episilon_transition['state'] not in visited:
                    queue.add(episilon_transition['state'])
            visited.add(state_number)

        return frozenset(closure)

    def get_epsilon_closures(self):
        """
        Return the list of epsilon surroundings for every state

        :return:
        """
        epsilon_dict = []
        for state_number in range(len(self.state_enumeration)):
            epsilon = self.epsilon_closure(state_number)

            epsilon_dict.append({'state': state_number, 'epsilon': epsilon})
        return epsilon_dict
