from ENKA import *
from StartSet import *

class DKA:
    """Izgradi DKA iz ENKA"""
    def __init__(self, productions, terminals, nonterminals):
        self.productions = productions
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.enka_utils = ENKA(self.productions,self.terminals,self.nonterminals)
        self.enka_transitions, self.enka_states = self.enka_utils.construct_enka_transitions()
        self.input_characters = self.terminals + self.nonterminals
    
    def epsilon_surrounding(self, starting_state, states, epsilon):
        
        if (not epsilon):
            return states
        else:
            epsilon = False
            delta = [starting_state,'$']
            test_values = filter(lambda x : x['delta']==delta, self.enka_transitions)
            test_values = list(test_values)
            if (len(test_values)!=0):
                epsilon = True
                for state in test_values:
                    state = state['state']
                    if state not in states:
                        states.append(state)
                        states = self.epsilon_surrounding(starting_state=state,states=states,epsilon=epsilon)
                return states

            return  self.epsilon_surrounding(starting_state=test_values,states=states,epsilon=epsilon)
        
    def epsilon_list(self):
        epsilon_dict = []
        for state in self.enka_states:
            epsilon = self.epsilon_surrounding(states=[state],starting_state=state,epsilon=True)
            dict_pair = {'state': state, 'epsilon': epsilon}
            epsilon_dict.append(dict_pair)
        return epsilon_dict
    
    def union_list_dict(self,list1,list2):
        union_list = list(list1)
        for el in list2:
            if el not in union_list:
                union_list.append(el)
        return union_list
    
    def enka_to_nka(self):

        nka_transitions = []
        epsilon_state_list = self.epsilon_list()
        for state in self.enka_states:
            inner_epsilon = list(filter(lambda x: x['state']==state, epsilon_state_list))[0]['epsilon']
            if state['production']['left'] == self.nonterminals[0]:
                state = inner_epsilon
            for char in self.input_characters:
                delta = [state,char]

                inner_states = []
                for inner_state in inner_epsilon:
                    transition_list = filter(lambda x: x['delta'][0]==inner_state and x['delta'][1]==char, self.enka_transitions)
                    transition_list = list(transition_list)
              
                    if len(transition_list)>0:
                        for transition in transition_list:
                            in_s = transition['state'] #podrazumijevam da nece za isto stanje i znak otici u vise moguca stanja (to je mozda greska)
                          
                            if in_s not in inner_states:
                                inner_states.append(in_s)
                output_states = []
                if len(inner_states) > 0:
                    for in_s in inner_states:
                        output_states = self.union_list_dict(output_states,list(filter(lambda x: x['state']==in_s, epsilon_state_list))[0]['epsilon'])
                    transition = {'delta':delta,'state': output_states}
                    nka_transitions.append(transition)
        return nka_transitions
    

    
    def nka_to_dka(self):
        nka_transitions = self.enka_to_nka()
        dka_transitions = list(nka_transitions)
        dka_states = [[state] for state in self.enka_states]
        dka_states[0]=(list(filter(lambda x: x['state']==dka_states[0][0], self.epsilon_list()))[0]['epsilon'])
        for transition in nka_transitions:
            input_state = transition['state']
            #print(f"input_states = {input_state}")
            state_in_check = list(filter(lambda x : x['delta'][0]==input_state, dka_transitions))
            if len(state_in_check)==0:
                for char in self.input_characters:
                    output = []
                    delta = [input_state,char]
                    for state in input_state:
                        
                        transition_state = list(filter(lambda x : x['delta']== [state,char],nka_transitions))
                        if len(transition_state)>0:
                            transition_state = [x['state'] for x in transition_state][0]
                            #print(f"transition_state: {transition_state}")
                        output = self.union_list_dict(output,transition_state)
                    if len(output)>0:
                        transition = {'delta':delta,'state':output}
                        #print(f"Appending transitions= {transition}")
                        dka_transitions.append(transition)
                        in_check = self.union_list_dict([transition['state']],[transition['delta'][0]])
                        dka_states = self.union_list_dict(dka_states,in_check)
        # for i in dka_transitions:
        #     print(f"DKA prijelaz = {i}\n")
        # print(len(dka_transitions))
        # print(f"\n DKA STATES : {dka_states}")
        return dka_transitions, dka_states

    
    def dka_minimizacija(self):
        dka_transitions, dka_states = self.nka_to_dka()
        state_numeric_dict  = {}
        num = 0
        dka_states_temp = list(dka_states)
        #ne uključujući početno stanje
        for states in dka_states_temp[1:]:
            # all transitions which end in states
            transitions_end = list(filter(lambda x: x['state']==states, dka_transitions))
            if len(transitions_end)==0 and states in dka_states:
                dka_states.remove(states)
        dka_transitions_temp = list(dka_transitions)
        for transition in dka_transitions_temp:
            if isinstance(transition['delta'][0],dict):
                same_char_state = list(filter(lambda x: isinstance(x['delta'][0],list) and transition['delta'][0] in x['delta'][0] and transition['state']==x['state'] and transition['delta'][1]==x['delta'][1],dka_transitions))
                if len(same_char_state)>0 and transition in dka_transitions:
                    dka_transitions.remove(transition)
               
                if  [transition['delta'][0]] in dka_states:
                    dka_states.remove([transition['delta'][0]])

        for i in range(len(dka_states)):
            state_numeric_dict[i]=dka_states[i]
        print(f"\n {state_numeric_dict}")
        for t in dka_transitions:
            state1 = t['delta'][0]
            state2 = t['state']
            if isinstance(state1,dict):
                state1 = [state1]
            key_state1 = [key for key, value in state_numeric_dict.items() if value == state1]
            key_state2 = [key for key, value in state_numeric_dict.items() if value == state2]
            
            t['state']= key_state2[0]
            t['delta'][0]=key_state1[0]
        
            
        print(state_numeric_dict)
        #preuredi dka_transitions
        for t in dka_transitions:
            print(f"transition : {t}")
        return state_numeric_dict, dka_transitions

       