from collections import deque
from helpers import *

class ActionsEnum:
    MOVE = 'move'
    REDUCE = 'reduce'
    ACCEPT = 'accept'


class Node:
    """Syntax Tree Node"""

    def __init__(self, values):
        self.values = values

    @classmethod
    def from_nodes(cls, nodes, value):
        """Create a node from child nodes by prepending whitespace to every child."""

        values = [value]

        for n in nodes:
            for value in n.values:
                values.append(' ' + value)

        return cls(values)


class LRParser:
    """LR Parser implementation."""

    def __init__(self, actions, new_states, sequence=''):
        """
        Initialize LR parser from the list of action, state transitions

        Parameters:
            actions (list[dict]): Actions of the parser (2D list)
            new_states (list[dict]): New states of the parser (2D list)
        """

        self.actions = actions
        self.new_states = new_states
        self.stack = deque([0])
        self.sequence = self.build_sequence(sequence)

    @classmethod
    def from_dfa(cls, dfa, productions):
        """
        Build LR parser from deterministic finite automata.

        :param dfa: DFA
        :return: LRParser
        """

        new_states = cls.build_new_states_table(dfa)
        actions = cls.build_actions_table(dfa, productions)

        return cls(actions, new_states)

    @classmethod
    def build_new_states_table(cls, dfa):
        """
        Build the new_states table from the given DFA.

        :param dfa: DFA
        :return: list[dict]
        """
        new_states = [{} for _ in range(len(dfa.state_productions))]
        for transition in dfa.transitions:
            if is_non_terminal(transition['delta'][1]):
                new_states[transition['delta'][0]][transition['delta'][1]] = transition['state']

        return new_states

    @classmethod
    def build_actions_table(cls, dfa, productions):
        """
        Build the actions table from the given DFA.

        :param dfa: DFA
        :return: list[dict]
        """

        actions = [{} for _ in range(len(dfa.state_productions))]
        for state, parser_items in enumerate(dfa.state_productions):
            for parser_item in parser_items:
                # print(state, parser_item)
                if parser_item['production']['right'][-1] == 0:
                    if parser_item['terminals'] == '!' and parser_item['production']['left'] == '<S0>':
                        actions[state]['!'] = {'type': ActionsEnum.ACCEPT }
                    else:
                        action = { 'type': ActionsEnum.REDUCE,
                          'left': parser_item['production']['left'],
                          'right':  parser_item['production']['right'][:-1] }

                        for terminal in parser_item['terminals']:
                            existing_action = actions[state].get(terminal)
                            actions[state][terminal] = cls.solve_ambiguity(action, existing_action, productions)
                else:
                    right = parser_item['production']['right']
                    next_symbol = right[right.index(0)+1]

                    if is_non_terminal(next_symbol):
                        continue

                    transition = next(filter(lambda x: x['delta'] == [state, next_symbol], dfa.transitions))
                    actions[state][next_symbol] = { 'type': ActionsEnum.MOVE, 'new_state': transition['state'] }

        return actions

    @classmethod
    def solve_ambiguity(cls, action_1, action_2, productions):
        """
        Resolve ambiguity when creating actions table using the following rules:
        1. MOVE is stronger than REDUCE
        2. if both are REDUCE, return the one defined earlier

        :param action_1:
        :param action_2:
        :param productions: Original grammar productions
        :return: dict
        """

        if action_1 is None: return action_2
        if action_2 is None: return action_1
        if action_1['type'] == ActionsEnum.MOVE: return action_1
        if action_2['type'] == ActionsEnum.MOVE: return action_2

        (action_1_copy := action_1.copy()).pop('type')
        (action_2_copy := action_2.copy()).pop('type')
        if productions.index(action_1_copy) < productions.index(action_2_copy):
            return action_1
        else:
            return action_2

    def init_stack(self):
        """
        Initialize the stack by setting the first (and only value) to zero.
        """

        self.stack = deque([0])

    def parse(self):
        """
        Parse the input sequence.

        Returns:
            True if the string is successfully parsed, False otherwise
        """
        if self.sequence[-1] != ['!']:
            self.sequence.append(['!'])
        
        while True:
            seq_element = self.sequence[0]
            current_state = self.stack[-1]

            action = self.actions[current_state].get(seq_element[0], None)
            if action is None:
                return False
            elif action['type'] == ActionsEnum.MOVE:
                self.stack.append(seq_element[0])
                self.stack.append(Node([' '.join(seq_element).strip()]))
                self.stack.append(action['new_state'])
                self.sequence = self.sequence[1:]
            elif action['type'] == ActionsEnum.REDUCE:
                if len(action['right']) == 0:
                    nodes = [Node(['$'])]
                else:
                    popped = self.pop_stack(len(action['right']))
                    nodes = reversed(list(filter(lambda x: type(x) == Node, popped)))

                current_state = self.stack[-1]
                self.stack.append(action['left'])
                self.stack.append(Node.from_nodes(nodes, action['left']))
                self.stack.append(self.new_states[current_state][action['left']])

            elif action['type'] == ActionsEnum.ACCEPT:
                return True

    def get_sequence(self):
        """
        Returns the unparsed part of the input sequence.
        """

        return list(map(lambda x: ' '.join(x), self.sequence))

    @staticmethod
    def build_sequence(raw_sequence):
        """
        Split each sequence element into two - element proper and element label. Perform the split on first whitespace.

        :param raw_sequence: list[string]
        :return: list[list]
        """
        return list(map(lambda x: x.split(' ', 1), raw_sequence))

    def set_sequence(self, raw_sequence):
        self.sequence = self.build_sequence(raw_sequence)

    def get_tree(self):
        """
        Returns the parse tree after a successful parse.
        """

        return '\n'.join(self.stack[-2].values)

    def pop_stack(self, n):
        return [self.stack.pop() for _ in range(3*n)]
