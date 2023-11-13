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
    def from_enka(cls, enfa):
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

            # print(*dka_transitions, sep='\n')
            transition['state'] = added.index(state_output)
            transition['delta'][0] = added.index(state_delta)

        return dka_transitions, state_productions
    
    @staticmethod
    def union_list_dict(list1, list2):
        union_list = list(list1)
        for el in list2:
            if el not in union_list:
                union_list.append(el)
        return union_list
    
    @classmethod
    def to_dfa(cls,enfa):
        dka_transitions = []
        # print(enfa.epsilon_closures)
        # print(enfa.state_enumeration)
        # print(enfa.transitions)
        start_state =  list(filter(lambda x: x['state'] == 0, enfa.epsilon_closures))[0]['epsilon']
        visited = [start_state] #na kraju ce ovo biti lista svih mogućih stanja
        queue = [start_state]
      
        while queue:
            state = queue.pop(0)
            for char in enfa.terminals + enfa.non_terminals:
                output = []
                delta = [state,char]
                for s in state:
                    transition_state = list(filter(lambda x : x['delta']== [s,char],enfa.transitions))
                    if len(transition_state)>0:
                        transition_state = [x['state'] for x in transition_state][0]
                        transition_state_epsilon = list(filter(lambda x: x['state'] == transition_state, enfa.epsilon_closures))[0]['epsilon']
                        output = cls.union_list_dict(output, transition_state_epsilon)
                if len(output)>0:
                    transition = {'delta':delta,'state':output}
                    dka_transitions.append(transition)
                    if output not in visited:
                        visited.append(output)
                        queue.append(output)


        return cls.numerate_states(enfa,dka_transitions)
    # def nfa_to_dfa(cls, nfa):
    #     """
    #     Convert NFA to DFA.

    #     :param nfa: NFA
    #     :return: DFA states and parser items list.
    #     """

    #     dka_transitions = []
    #     dka_start_state = nfa.epsilon_closures[0]['epsilon']
    #     visited = []
    #     queue = [dka_start_state]
    #     while queue:
    #         current_state = queue.pop(0)
    #         transitions_from_state = list(filter(lambda x: x['delta'][0] in current_state, nfa.transitions))
    #         for symbol in nfa.terminals + nfa.non_terminals:
    #             new_state = set(chain.from_iterable(map(lambda x: x['state'],
    #                                                 filter(lambda x: x['delta'][1] == symbol, transitions_from_state))))

    #             dka_transition = { 'delta': [current_state, symbol], 'state': new_state }
    #             if len(new_state) != 0 and dka_transition not in dka_transitions:
    #                 dka_transitions.append(dka_transition)
    #                 if new_state not in visited and len(new_state) != 0:
    #                     queue.append(new_state)
    #         visited.append(current_state)

    #     return cls.numerate_states(nfa, dka_transitions)
  