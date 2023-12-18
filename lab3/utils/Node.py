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
        self.value = self._parse_value(value, name)
        self.parent = None
        self.children = []
        self.scope = None

    @staticmethod
    def _parse_value(value, name):
        """
        Character (ZNAK) and String (NIZ_ZNAKOVA) constants are read with quotation marks, this method removed them.
        """

        if name == 'ZNAK' or name == 'NIZ_ZNAKOVA':
            return value[1:-1]
        return value

    def set_parent(self, parent):
        self.parent = parent

    def get_declaration(self, identifier: str, max_levels=-1, only_global: bool = False):
        if only_global:
            return self._get_global_declaration(identifier)
        else:
            return self._get_declaration(identifier, max_levels)

    def _get_global_declaration(self, identifier: str):
        """
        Get declaration from the global (top-level) context exclusively.

        :return: declaration, if exists, None otherwise.
        """

        parent = self.parent
        while parent.parent:
            parent = parent.parent

        if parent.scope is None:
            return None

        for declaration in parent.scope.declarations:
            if declaration['identifier'] == identifier:
                return declaration

        return None

    def _get_declaration(self, identifier: str, max_levels=-1):
        """
        Get declaration from the scope at most max_levels above current node.

        :return: declaration, if exists, None otherwise.
        """

        levels = 0
        node = self
        while node := node.parent:
            if node.parent and node.name != Scope.LOCAL_SCOPE_NODE:
                continue

            if node.scope:
                for declaration in node.scope.declarations:
                    if declaration['identifier'] == identifier:
                        return declaration

            levels += 1
            if levels == max_levels:
                return None

    def declare_variable(self, identifier: str, variable_type: str):
        """
        Add variable declaration to the first scope above, regardless if it is global or local.
        """

        node = self
        while node.parent and node.name != Scope.LOCAL_SCOPE_NODE:
            node = node.parent

        if node.scope is None:
            node.scope = Scope()

        node.scope.add_declaration({
            'identifier': identifier,
            'return_type': variable_type,
            'kind': 'variable'
        })

    def declare_function(self, identifier: str, parameter_types: list[str], return_type: str,
                         definition: bool = False):
        """
        Add function declaration to the first scope above, if declaration is NOT a definition. Definitions are added to
        the global scope.
        """

        node = self.parent
        while node.parent and (definition or node.name != Scope.LOCAL_SCOPE_NODE):
            node = node.parent

        if node.scope is None:
            node.scope = Scope()

        declaration = {
            'identifier': identifier,
            'parameter_types': parameter_types,
            'return_type': return_type,
            'kind': 'function',
            'definition': definition
        }
        node.scope.add_declaration(declaration)

        return declaration
