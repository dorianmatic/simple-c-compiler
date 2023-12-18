import fileinput
from utils.Tree import build_tree, print_tree

if __name__ == '__main__':
    lines = []

    for line in fileinput.input():
        lines.append(line)

    tree = build_tree(lines)

    print_tree(tree)