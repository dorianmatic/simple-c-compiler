from Node import Node

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
    if node.scope != None:
        print(node.scope.declarations)
    else:
        print(node.scope)
    print(node.value)
    for child in node.children:
        print_tree(child, indent + 1)
