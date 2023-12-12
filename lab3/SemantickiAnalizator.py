import fileinput
from utils.tree import build_tree, print_tree
from utils.RecursiveDescent import RecursiveDescent, DescentException

if __name__ == '__main__':
    lines = []

    for line in fileinput.input():
        lines.append(line)

    tree = build_tree(lines)
    recursive_descent = RecursiveDescent(tree)

    try:
        recursive_descent.descend()
    except DescentException as de:
        print(de)

    print_tree(tree)