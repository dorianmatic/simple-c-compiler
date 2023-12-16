from lab3.utils.helpers import *
from lab3.utils.Scope import Scope

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
        self.scope = None # Used in Recursive Descent

    def set_parent(self, parent):
        self.parent = parent

    def set_scope(self, scope: Scope):
        self.scope = scope