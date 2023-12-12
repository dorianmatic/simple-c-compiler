from lab3.utils.helpers import *

class Node:
    def __init__(self, content: str):
        content = content.split(' ')

        name = content[0]
        if is_non_terminal(content[0]):
            line = None
            value = None
        else:
            line = int(content[1])
            value = content[2]

        self.name = name
        self.line = line
        self.value = value
        self.parent = None
        self.children = []

    def set_parent(self, parent):
        self.parent = parent

def build_tree(lines):
    last_at_level = []

    for line in lines:
        new_node = Node(line.strip())
        n_spaces = len(line) - len(line.lstrip())

        if n_spaces > 0:
            new_node.set_parent(last_at_level[n_spaces - 1])
            last_at_level[n_spaces - 1].children.append(new_node)

        if n_spaces - len(last_at_level) < 0:
            last_at_level[n_spaces] = new_node
        elif n_spaces == len(last_at_level):
            last_at_level.append(new_node)

    return last_at_level[0]


def print_tree(node: Node, indent=0):
    print(' ' * indent + node.name)

    for child in node.children:
        print_tree(child, indent + 1)
