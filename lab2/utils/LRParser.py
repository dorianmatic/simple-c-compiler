from collections import deque


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

    def __init__(self, actions, new_states, sequence):
        """
        Initialize LR parser from the list of action, state transitions

        Parameters:
            actions (list[map]): Actions of the parser (2D list)
            new_states (list[map]): New states of the parser (2D list)
        """

        self.actions = actions
        self.new_states = new_states
        self.stack = deque([0])
        self.sequence = sequence

    @classmethod
    def from_dsa(cls, dsa):
        pass

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

        if self.sequence[-1] != '$':
            self.sequence.append('$')
        
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
