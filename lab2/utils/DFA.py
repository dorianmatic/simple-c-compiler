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
    def from_nka(cls, nfa):
        """
        Initialize DFA from non-deterministic finite state automata.

        :param nfa:
        :return: DFA
        """

        dka_transitions, state_productions = cls.nfa_to_dfa(nfa)

        return cls(dka_transitions, state_productions)

    @classmethod
    def numerate_states(cls, nfa, dka_transitions):
        """Numerates the states and add the number,state pair to the state_productions"""
       
        state_productions = []
        added = []
        for transition in dka_transitions:
            if (state_delta := transition['delta'][0]) not in added:
                state_productions.append(list(map(lambda x: nfa.state_enumeration[x], state_delta)))
                added.append(state_delta)

            if (state_output := transition['state']) not in added:
                state_productions.append(list(map(lambda x: nfa.state_enumeration[x], state_output)))
                added.append(state_output)

            # print(*dka_transitions, sep='\n')
            transition['state'] = added.index(state_output)
            transition['delta'][0] = added.index(state_delta)

        return dka_transitions, state_productions

    @classmethod
    def nfa_to_dfa(cls, nfa):
        """
        Convert NFA to DFA.

        :param nfa: NFA
        :return: DFA states and parser items list.
        """

        dka_transitions = []
        dka_start_state = nfa.epsilon_closures[0]['epsilon']
        visited = []
        queue = [dka_start_state]
        while queue:
            current_state = queue.pop(0)
            transitions_from_state = list(filter(lambda x: x['delta'][0] in current_state, nfa.transitions))
            for symbol in nfa.terminals + nfa.non_terminals:
                new_state = set(chain.from_iterable(map(lambda x: x['state'],
                                                    filter(lambda x: x['delta'][1] == symbol, transitions_from_state))))

                dka_transition = { 'delta': [current_state, symbol], 'state': new_state }
                if len(new_state) != 0 and dka_transition not in dka_transitions:
                    dka_transitions.append(dka_transition)
                    if new_state not in visited:
                        queue.append(new_state)
            visited.append(current_state)

        return cls.numerate_states(nfa, dka_transitions)
  