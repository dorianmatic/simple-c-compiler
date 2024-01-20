from ENKA import *
from StartSet import *
import itertools

class DKA:
    """Izgradi DKA iz ENKA"""
    def __init__(self, productions, terminals, nonterminals):
        self.productions = productions
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.enka_utils = ENKA(self.productions,self.terminals,self.nonterminals)
        self.enka_transitions, self.enka_states = self.enka_utils.construct_enka_transitions()
        self.input_characters = self.terminals + self.nonterminals
        self.epsilon_list = self.get_epsilon_list()
        self.dka_start_state = list(filter(lambda x: x['state']==self.enka_states[0], self.epsilon_list))[0]['epsilon']
        print(self.enka_states)
    
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
        
    def get_epsilon_list(self):
        epsilon_dict = []
        for state in self.enka_states:
            epsilon = self.epsilon_surrounding(states=[state],starting_state=state,epsilon=True)
            dict_pair = {'state': state, 'epsilon': epsilon}
            epsilon_dict.append(dict_pair)
        return epsilon_dict
    
    #ova union funkcija je upitna dosta
    def union_list_dict(self,list1,list2):
        union_list = list(list1)
        for el in list2:
            if el not in union_list:
                union_list.append(el)
        return union_list
    
    def enka_to_nka(self):

        nka_transitions = []
        epsilon_state_list = self.epsilon_list
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
    
    def numerate_states(self, dka_transitions):
        """Numerates the states and add the number,state pair to the state_numeric_dict"""
       
        state_numeric_dict = {0:self.dka_start_state}
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
    
    def nka_to_dka(self):
        nka_transitions = self.enka_to_nka()
        ##implement bfs = no need for unreachable search, only checking for redundant states later on
        dka_transitions = []

        visited = [self.dka_start_state]
        queue = [self.dka_start_state]
        while queue:
            input_state = queue.pop(0)
            #naprvai kaj zelis s njegovim tranzicijama = dodaj u dka_transitions
            transitions_for_state = list(filter(lambda x: x['delta'][0]==input_state,nka_transitions))

            #ako postoje vec prijelazi za to stanje
            if len(transitions_for_state)>0:
                dka_transitions.extend(transitions_for_state)
                for transition in transitions_for_state:
                    new_state = transition['state']
                    if new_state not in visited:
                        visited.append(new_state)
                        queue.append(new_state)
            else:
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
                        if output not in visited:
                            visited.append(output)
                            queue.append(output)

        dka_transitions,state_numeric_dict = self.numerate_states(dka_transitions)

        for i in dka_transitions:
           print(f"DKA prijelaz = {i}\n")
        print(state_numeric_dict)
        return dka_transitions, state_numeric_dict

    def intersection_list_dict(list1, list2):
        set1 = {frozenset(d.items()) for d in list1}
        set2 = {frozenset(d.items()) for d in list2}
        
        intersection = set1.intersection(set2)
        
        result = [dict(items) for items in intersection]
    
        return result
    
    def out_of_reach(self,dka_transactions,input,states,start_state):
        NDS = []
        TF = {}
        DS = [start_state]
        for s in states:
            if(s in DS):
                TF[s]=True
            else:
                TF[s]=False
        nova = []
        for s in DS:
            nova.append(s)
        while(len(nova)!=0):
            s = nova.pop()
            for a in input:
                delta = [s,a]
                output = list(filter(lambda x:x['delta']==delta,dka_transactions))
                if len(output)>0:
                    output = output[0]['state']
                    if(TF.get(output)==False):
                        nova.append(output)
                        TF[output]=True
                        DS.append(output)
        for s in states:
            if(s not in DS):
                NDS.append(s)
        return NDS

    def dka_minimizacija(self):
        #izbaci nedostižna stanja!!!! i onda pogledaj kaj se desi (poslije implement istovjetnost ako je potrebno)
        dka_transitions, state_numeric_dict = self.nka_to_dka()
        input_characters = self.nonterminals + self.terminals
        unreachable_states = self.out_of_reach(dka_transitions,input_characters,list(state_numeric_dict.keys()),0)
        print(f"\n {unreachable_states}")
        for transition in dka_transitions:
            if transition['delta'][0] in unreachable_states:
                dka_transitions.remove(transition)
        #Sva stanja koja za iste ulaze idu u ista stanja su istovjetna
        # for state in state_numeric_dict.keys():
        #     transition_targets = list(filter(lambda x : x['delta'][0]==[state],dka_transitions))
        #     equivalent_states = []
        #     for transition in transition_targets:
        #         equivalent = [state['delta'][0] for state in list(filter(lambda x:x['delta'][1]==transition['delta'][1] and x['delta'][0]!=state and x['state']==transition['state'],dka_transitions))]
        #         equivalent_states = self.intersection_list_dict(equivalent_states,equivalent)
            
        #     #naprvaiti union među ekvivalentnim stanjima
        #     union_ultimate_state = []
        #     for e in equivalent_states:
        #         state = state_numeric_dict[e]
        #         dka_transitions.remove(transition)
        #         union_ultimate_state = self.union_list_dict(union_ultimate_state,state)
        #     if len(union_ultimate_state)>0:
        #         #nastavi algoritam iako je maybe beskoristan za svaki slucaj da bude tu
        #         return

        for t in dka_transitions:
            print(f"transition : {t}")
        print(state_numeric_dict)
        return dka_transitions,state_numeric_dict

       