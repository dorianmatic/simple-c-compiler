from lab2.utils.StartSet import *


class ENKA:
    """Na temelju produkcija gramatike, nezavrsnih i zavrsnih znakova se gradi ENKA"""

    def __init__(self, productions, terminals, nonterminals):
        self.productions = productions
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.start_utils = Zapocinje(
            self.productions, self.terminals, self.nonterminals
        )

    def get_states(self):
        states = []
        for production in self.productions:
            left = production["left"]
            right = production["right"]
            if right == ["$"]:
                right = []
            right_LR = list(right)
            for i in range(len(right) + 1):
                right_LR.insert(i, 0)
                state = {"left": left, "right": right_LR}
                states.append(state)
                right_LR = list(right)

        return states

    def find_terminals(self, parser_read_point, right_current_state, current_state):
        if parser_read_point + 2 < len(right_current_state):
            zapocni_characters = right_current_state[parser_read_point + 2 :]
            terminals = self.start_utils.start_union(zapocni_characters)
            if self.start_utils.generate_empty(zapocni_characters):
                terminals = terminals + list(current_state["terminals"])
        else:
            terminals = current_state["terminals"]

        return terminals

    def bfs_check(self, visited, queue, transitions, transition, state_with_terminals):
        if transition['state'] not in state_with_terminals:
            state_with_terminals.append(transition['state'])
        if transition["state"] not in visited:
            visited.append(transition["state"])
            queue.append(transition["state"])
        transitions.append(transition)
        return transitions, queue, visited, state_with_terminals

    def construct_enka_transitions(self):
        states = self.get_states()
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
                input = right_current_state[parser_read_point + 1]
                delta = [current_state, input]
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
                
                transitions, queue, visited, state_with_terminals = self.bfs_check(
                    visited, queue, transitions, transition, state_with_terminals
                )

                epsilon_transition_states = [
                    state
                    for state in states
                    if state["left"] == input and state["right"][0] == 0
                ]
                for state in epsilon_transition_states:
                    delta = [current_state, "$"]
                    terminals = self.find_terminals(
                        parser_read_point, right_current_state, current_state
                    )
                    transition = {
                        "delta": delta,
                        "state": {"production": state, "terminals": terminals},
                    }
                    transitions, queue, visited, state_with_terminals = self.bfs_check(
                        visited, queue, transitions, transition, state_with_terminals
                    )

        return transitions, state_with_terminals
