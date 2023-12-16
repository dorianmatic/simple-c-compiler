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

    def get_declaration(self, identifier: str, max_levels=-1, only_global: bool = False):
        if only_global:
            return self._get_global_declaration(identifier)
        else:
            return self._get_declaration(identifier, max_levels)

    def _get_global_declaration(self, identifier: str):
        parent = self.parent
        while parent.name != Scope.GLOBAL_SCOPE_NODE:
            parent = parent.parent

        if parent.scope is None:
            return None

        for declaration in parent.scope.declarations:
            if declaration['identifier'] == identifier:
                return declaration

        return None

    def _get_declaration(self, identifier: str, max_levels=-1):
        levels = 0
        node = self
        while True:
            node = node.parent
            if node is None or levels == max_levels:
                return None
            if node.scope is None:
                continue

            for declaration in node.scope.declarations:
                if declaration['identifier'] == identifier:
                    return declaration

            levels += 1

    def declare_variable(self, identifier: str, variable_type: str):
        node = self
        while node.name != Scope.GLOBAL_SCOPE_NODE and node.name != Scope.LOCAL_SCOPE_NODE:
            node = node.parent

        if node.scope is None:
            node.create_scope(Scope())

        node.scope.add_declaration({
            'identifier': identifier,
            'type': variable_type,
            'kind': 'variable'
        })

    def declare_function(self, identifier: str, parameter_types: list[str], return_type: str,
                         definition: bool = False):
        node = self.parent
        while node.name != Scope.GLOBAL_SCOPE_NODE:
            node = node.parent

        if node.scope is None:
            node.scope = Scope()

        node.scope.add_declaration({
            'identifier': identifier,
            'parameter_types': parameter_types,
            'return_type': return_type,
            'kind': 'function',
            'definition': definition
        })
