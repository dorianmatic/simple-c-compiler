import fileinput
from lab4.utils.generative_tree import build_tree
from RecursiveDescent import RecursiveDescent, DescentException


def main():
    lines = []

    for line in fileinput.input():
        lines.append(line)

    tree = build_tree(lines)
    recursive_descent = RecursiveDescent(tree)

    try:
        recursive_descent.descend()
    except DescentException as de:
        return
    
    return tree
        
main()
    
    
    
