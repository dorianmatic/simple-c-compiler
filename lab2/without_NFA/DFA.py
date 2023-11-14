from itertools import chain


class DFA:
    """Deterministic finite state automata for LR parser."""

    def __init__(self, transitions, state_productions):
        """
        Initialize DFA from transitions and parser items dictionary.

        :param transitions: DFA transitions list.
        :param state_numeric_dict:
        """
        self.transitions = transitions
        self.state_productions = state_productions

    @classmethod
    def from_enfa(cls, enfa):
        """
        Initialize DFA from non-deterministic finite state automata.

        :param nfa:
        :return: DFA
        """

        dka_transitions, state_productions = cls.to_dfa(enfa)
        return cls(dka_transitions, state_productions)

    @classmethod
    def numerate_states(cls, enfa, dka_transitions):
        """Numerates the states and add the number,state pair to the state_productions"""

        state_productions = []
        added = []
        for transition in dka_transitions:
            if (state_delta := transition['delta'][0]) not in added:
                state_productions.append(list(map(lambda x: enfa.state_enumeration[x], state_delta)))
                added.append(state_delta)

            if (state_output := transition['state']) not in added:
                state_productions.append(list(map(lambda x: enfa.state_enumeration[x], state_output)))
                added.append(state_output)

            transition['state'] = added.index(state_output)
            transition['delta'][0] = added.index(state_delta)

        return dka_transitions, state_productions

    @classmethod
    def to_dfa(cls, enfa):
        dka_transitions = []
        start_state = enfa.epsilon_closures[0]['epsilon']
        visited = set()
        queue = {start_state}

        while queue:
            state = queue.pop()
            print('-------------', state)
            for symbol in enfa.terminals + enfa.non_terminals:
                # output = chain.from_iterable(map(lambda x: enfa.epsilon_closures[x[0]['state']]['epsilon'] if x else [],
                #                                  map(lambda x: enfa.find_transitions(x, symbol),
                #                                      state)))

                output = chain.from_iterable(map(lambda x: enfa.find_closure_for_transition(x, symbol), state))
                output = frozenset(output)
                if output:
                    dka_transitions.append({'delta': [state, symbol], 'state': output})
                    if output not in visited and output not in queue:
                        queue.add(output)

            visited.add(state)
        return cls.numerate_states(enfa, dka_transitions)
