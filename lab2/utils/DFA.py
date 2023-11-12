class DFA:
    """Deterministic finite state automata for LR parser."""

    def __init__(self, transitions, state_numeric_dict):
        """
        Initialize DFA from transitions and parser items dictionary.

        :param transitions: DFA transitions list.
        :param state_numeric_dict:
        """
        self.transitions = transitions
        self.state_numeric_dict = state_numeric_dict

    @classmethod
    def from_nka(cls, nfa):
        """
        Initialize DFA from non-deterministic finite state automata.

        :param nfa:
        :return: DFA
        """

        dka_transitions, state_numeric_dict = cls.nfa_to_dfa(nfa)

        return cls(dka_transitions, state_numeric_dict)

    @classmethod
    def numerate_states(cls, dka_transitions, start_state):
        """Numerates the states and add the number,state pair to the state_numeric_dict"""
       
        state_numeric_dict = {0: start_state}
        num = 1
        for transition in dka_transitions:
            state_delta = transition['delta'][0] if isinstance(transition['delta'][0],list) else [transition['delta'][0]]
            state_output = transition['state']
            if state_output not in state_numeric_dict.values():
                state_numeric_dict[num]=state_output
                num += 1
            if state_delta not in state_numeric_dict.values():
                state_numeric_dict[num]=state_delta
                num += 1
            transition['state']=[key for key, value in state_numeric_dict.items() if value == state_output][0]
            transition['delta'][0]=[key for key, value in state_numeric_dict.items() if value == state_delta][0]
        return dka_transitions, state_numeric_dict

    @staticmethod
    def union_list_dict(list1, list2):
        union_list = list(list1)
        for el in list2:
            if el not in union_list:
                union_list.append(el)
        return union_list

    @classmethod
    def nfa_to_dfa(cls, nfa):
        """
        Convert NFA to DFA.

        :param nfa: NFA
        :return: DFA states and parser items dictionary.
        """

        dka_transitions = []

        dka_start_state = list(filter(lambda x: x['state'] == nfa.state_with_terminals[0], nfa.epsilon_closures))[0]['epsilon']
        visited = [dka_start_state]
        queue = [dka_start_state]
        while queue:
            input_state = queue.pop(0)
            transitions_for_state = list(filter(lambda x: x['delta'][0]==input_state, nfa.transitions))

            if len(transitions_for_state)>0:
                dka_transitions.extend(transitions_for_state)
                for transition in transitions_for_state:
                    new_state = transition['state']
                    if new_state not in visited:
                        visited.append(new_state)
                        queue.append(new_state)
            else:
                for char in nfa.terminals + nfa.non_terminals:
                    output = []
                    delta = [input_state,char]
                    for state in input_state:
                                
                        transition_state = list(filter(lambda x : x['delta']== [state,char], nfa.transitions))
                        if len(transition_state)>0:
                            transition_state = [x['state'] for x in transition_state][0]
                        output = cls.union_list_dict(output, transition_state)
                    if len(output)>0:
                        transition = {'delta':delta,'state':output}
                        dka_transitions.append(transition)
                        if output not in visited:
                            visited.append(output)
                            queue.append(output)

        return cls.numerate_states(dka_transitions, dka_start_state)
  