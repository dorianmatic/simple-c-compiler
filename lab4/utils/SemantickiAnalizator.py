import fileinput
from generative_tree import build_tree
from RecursiveDescent import RecursiveDescent, DescentException
from Node import Node

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
    
    
    
