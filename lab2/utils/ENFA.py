from lab2.utils.StartSet import *


class ENFA:
    """Non-deterministic finite state automata with (or without) epsilon-transitions."""

    def __init__(self, transitions, states, state_with_terminals, terminals, non_terminals):
        self.transitions = transitions
        self.states = states
        self.state_with_terminals = state_with_terminals
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.epsilon_list = self.get_epsilon_list()

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
        start_utils = Zapocinje(productions, terminals, non_terminals)
        transitions, state_with_terminals = cls.construct_enka_transitions(states, start_utils)

        return cls(transitions, states, state_with_terminals, terminals, non_terminals)

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
    def bfs_check(cls, visited, queue, transitions, transition, state_with_terminals):
        if transition['state'] not in state_with_terminals:
            state_with_terminals.append(transition['state'])
        if transition["state"] not in visited:
            visited.append(transition["state"])
            queue.append(transition["state"])
        transitions.append(transition)

        return transitions, queue, visited, state_with_terminals

    @classmethod
    def construct_enka_transitions(cls, states, start_utils):
        state_0 = {"production": states[0], "terminals": "!"}
        state_with_terminals = [state_0]
        transitions = []
        queue = [state_0]
        visited = [state_0]

        while queue:
            current_state = queue.pop(0)
            right_current_state = current_state["production"]["right"]
            parser_read_point = right_current_state.index(0)

            if parser_read_point + 1 < len(right_current_state):
                inp = right_current_state[parser_read_point + 1]
                delta = [current_state, inp]
                new_right_state = list(right_current_state)
                new_right_state.remove(0)
                new_right_state.insert(parser_read_point + 1, 0)
                input_transition_state = {
                    "left": current_state["production"]["left"],
                    "right": new_right_state,
                }

                transition = {
                    "delta": delta,
                    "state": {
                        "production": input_transition_state,
                        "terminals": current_state["terminals"],
                    },
                }
                
                transitions, queue, visited, state_with_terminals = cls.bfs_check(
                    visited, queue, transitions, transition, state_with_terminals
                )

                epsilon_transition_states = [
                    state
                    for state in states
                    if state["left"] == inp and state["right"][0] == 0
                ]
                for state in epsilon_transition_states:
                    delta = [current_state, "$"]
                    terminals = cls.find_terminals(right_current_state[parser_read_point+2:], current_state, start_utils)
                    transition = {
                        "delta": delta,
                        "state": {"production": state, "terminals": terminals},
                    }
                    transitions, queue, visited, state_with_terminals = cls.bfs_check(
                        visited, queue, transitions, transition, state_with_terminals
                    )

        return transitions, state_with_terminals


    # ova union funkcija je upitna dosta
    @staticmethod
    def union_list_dict(list1, list2):
        union_list = list(list1)
        for el in list2:
            if el not in union_list:
                union_list.append(el)
        return union_list

    def epsilon_surrounding(self, starting_state, states, epsilon):
        if not epsilon:
            return states
        else:
            epsilon = False
            delta = [starting_state, '$']
            test_values = filter(lambda x: x['delta'] == delta, self.transitions)
            test_values = list(test_values)
            if len(test_values) != 0:
                epsilon = True
                for state in test_values:
                    state = state['state']
                    if state not in states:
                        states.append(state)
                        states = self.epsilon_surrounding(starting_state=state, states=states, epsilon=epsilon)
                return states

            return self.epsilon_surrounding(starting_state=test_values, states=states, epsilon=epsilon)

    def get_epsilon_list(self):
        epsilon_dict = []
        for state in self.state_with_terminals:
            epsilon = self.epsilon_surrounding(states=[state], starting_state=state, epsilon=True)
            dict_pair = {'state': state, 'epsilon': epsilon}
            epsilon_dict.append(dict_pair)
        return epsilon_dict

    def to_nka(self):
        """Convert ENFA to NFA by removing epsilon-transitions."""

        nka_transitions = []
        for state in self.state_with_terminals:
            inner_epsilon = list(filter(lambda x: x['state'] == state, self.epsilon_list))[0]['epsilon']
            if state['production']['left'] == self.non_terminals[0]:
                state = inner_epsilon
            for char in self.terminals + self.non_terminals:
                delta = [state, char]

                inner_states = []
                for inner_state in inner_epsilon:
                    transition_list = filter(lambda x: x['delta'][0] == inner_state and x['delta'][1] == char,
                                             self.transitions)
                    transition_list = list(transition_list)

                    if len(transition_list) > 0:
                        for transition in transition_list:
                            in_s = transition['state']  # podrazumijevam da nece za isto stanje i znak otici u vise moguca stanja (to je mozda greska)

                            if in_s not in inner_states:
                                inner_states.append(in_s)

                output_states = []
                if len(inner_states) > 0:
                    for in_s in inner_states:
                        output_states = self.union_list_dict(output_states, list(
                            filter(lambda x: x['state'] == in_s, self.epsilon_list))[0]['epsilon'])
                    transition = {'delta': delta, 'state': output_states}
                    nka_transitions.append(transition)

        self.transitions = nka_transitions