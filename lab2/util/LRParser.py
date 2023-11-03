from collections import deque


class ActionsEnum:
    MOVE = 'move'
    REDUCE = 'reduce'
    ACCEPT = 'accept'


class Node:
    def __init__(self, values):
        self.values = values

    @classmethod
    def from_nodes(cls, nodes, value):
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

    def parse(self, string, tree=False):
        """
        Parse the input string.
        """

        string = string + ['$']
        stack = deque([0])
        
        while True:
            a = string[0]
            s = stack[-1]

            action = self.actions[s].get(a, None)
            if action is None:
                return False
            elif action['type'] == ActionsEnum.MOVE:
                stack.append(a)
                stack.append(Node([a]))
                stack.append(action['new_state'])
                string = string[1:]
            elif action['type'] == ActionsEnum.REDUCE:
                popped = [stack.pop() for _ in range(3*len(action['right']))]
                nodes = filter(lambda x: type(x) == Node, popped)

                s = stack[-1]
                stack.append(action['left'])
                stack.append(Node.from_nodes(nodes, action['left']))
                stack.append(self.new_states[s][action['left']])

            elif action['type'] == ActionsEnum.ACCEPT:
                if tree:
                    return '\n'.join(stack[-2].values)
                else:
                    return True
