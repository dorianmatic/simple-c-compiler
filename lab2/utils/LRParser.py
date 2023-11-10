from collections import deque


class ActionsEnum:
    MOVE = 'move'
    REDUCE = 'reduce'
    ACCEPT = 'accept'

def is_non_terminal(symbol):
    return symbol.startswith('<') and symbol.endswith('>')

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
        self.sequence = sequence

    @classmethod
    def from_dfa(cls, dfa):
        """
        Build LR parser from deterministic finite automata.

        :param dfa: DFA
        :return: LRParser
        """

        new_states = cls.build_new_states_table(dfa)
        actions = cls.build_actions_table(dfa)

        return cls(actions, new_states)

    @classmethod
    def build_new_states_table(cls, dfa):
        """
        Build the new_states table from the given DFA.

        :param dfa: DFA
        :return: list[dict]
        """
        new_states = [{} for _ in range(len(dfa.state_numeric_dict))]
        for transition in dfa.transitions:
            if is_non_terminal(transition['delta'][1]):
                new_states[transition['delta'][0]][transition['delta'][1]] = transition['state']

        return new_states

    @classmethod
    def build_actions_table(cls, dfa):
        """
        Build the actions table from the given DFA.

        :param dfa: DFA
        :return: list[dict]
        """
        actions = [{} for _ in range(len(dfa.state_numeric_dict))]
        for state, parser_items in dfa.state_numeric_dict.items():
            for parser_item in parser_items:
                if parser_item['production']['right'][-1] == 0:
                    if parser_item['terminals'] == '!' and parser_item['production']['left'] == '<S0>':
                        actions[state]['!'] = {'type': ActionsEnum.ACCEPT }
                    else:
                        action = { 'type': ActionsEnum.REDUCE,
                          'left': parser_item['production']['left'],
                          'right':  parser_item['production']['right'][:-1] }

                        for terminal in parser_item['terminals']:
                            actions[state][terminal] = action
                else:
                    right = parser_item['production']['right']
                    next_symbol = right[right.index(0)+1]

                    if is_non_terminal(next_symbol):
                        continue

                    transition = next(filter(lambda x: x['delta'] == [state, next_symbol], dfa.transitions))
                    actions[state][next_symbol] = { 'type': ActionsEnum.MOVE, 'new_state': transition['state'] }

        return actions

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

        if self.sequence[-1] != '!':
            self.sequence.append('!')
        
        while True:
            seq_element = self.sequence[0]
            current_state = self.stack[-1]

            action = self.actions[current_state].get(seq_element, None)
            if action is None:
                return False
            elif action['type'] == ActionsEnum.MOVE:
                self.stack.append(seq_element)
                self.stack.append(Node([seq_element]))
                self.stack.append(action['new_state'])
                self.sequence = self.sequence[1:]
            elif action['type'] == ActionsEnum.REDUCE:
                popped = [self.stack.pop() for _ in range(3*len(action['right']))]
                nodes = filter(lambda x: type(x) == Node, popped)

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

        return self.sequence

    def set_sequence(self, sequence):
        self.sequence = sequence

    def get_tree(self):
        """
        Returns the parse tree after a successful parse.
        """

        return '\n'.join(self.stack[-2].values)
