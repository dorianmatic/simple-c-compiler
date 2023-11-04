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

    def __init__(self, actions, new_states):
        """
        Initialize LR parser from the list of action, state transitions

        Parameters:
            actions (list[map]): Actions of the parser (2D list)
            new_states (list[map]): New states of the parser (2D list)
        """

        self.actions = actions
        self.new_states = new_states
        self.stack = deque([0])

    def init_stack(self):
        """
        Initialize the stack by setting the first (and only value) to zero.
        """

        self.stack = deque([0])

    def parse(self, string, tree=False):
        """
        Parse the input string.
        """

        string = string + ['$']
        
        while True:
            a = string[0]
            s = self.stack[-1]

            action = self.actions[s].get(a, None)
            if action is None:
                return False
            elif action['type'] == ActionsEnum.MOVE:
                self.stack.append(a)
                self.stack.append(Node([a]))
                self.stack.append(action['new_state'])
                string = string[1:]
            elif action['type'] == ActionsEnum.REDUCE:
                popped = [self.stack.pop() for _ in range(3*len(action['right']))]
                nodes = filter(lambda x: type(x) == Node, popped)

                s = self.stack[-1]
                self.stack.append(action['left'])
                self.stack.append(Node.from_nodes(nodes, action['left']))
                self.stack.append(self.new_states[s][action['left']])

            elif action['type'] == ActionsEnum.ACCEPT:
                if tree:
                    return '\n'.join(self.stack[-2].values)
                else:
                    return True
