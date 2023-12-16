from lab3.utils.Node import Node


class Scope:
    GLOBAL_SCOPE_NODE = '<prijevodna_jedinica>'
    LOCAL_SCOPE_NODE = '<slozena_naredba>'

    def __init__(self):
        self.declarations = []

    def get_definition_identifiers(self):
        return list(map(lambda x: x['identifier'], self.declarations))

    @classmethod
    def get_declaration(cls, node: Node, identifier: str, max_levels=-1, only_global: bool = False):
        if only_global:
            return cls._get_global_declaration(node, identifier)
        else:
            return cls._get_declaration(node, identifier, max_levels)

    @classmethod
    def _get_global_declaration(cls, node: Node, identifier: str):
        parent = node.parent
        while parent.name != cls.GLOBAL_SCOPE_NODE:
            parent = parent.parent

        for declaration in parent.scope.declarations:
            if declaration['identifier'] == identifier:
                return declaration

        return None

    @classmethod
    def _get_declaration(cls, node: Node, identifier: str, max_levels=-1):
        levels = 0
        while True:
            current_node = node.parent
            if current_node is None or levels == max_levels:
                return None
            if current_node.scope is None:
                continue

            for declaration in current_node.scope.declarations:
                if declaration['identifier'] == identifier:
                    return declaration

            levels += 1

    @classmethod
    def declare_variable(cls, node: Node, identifier: str, variable_type: str):
        while node.name != cls.GLOBAL_SCOPE_NODE and node.name != cls.LOCAL_SCOPE_NODE:
            node = node.parent

        if node.scope is None:
            node.set_scope(Scope())

        node.scope.defintions.append({
            'identifier': identifier,
            'type': variable_type,
            'kind': 'variable'
        })

    @classmethod
    def declare_function(cls, node: Node, identifier: str, parameter_types: list[str], return_type: str,
                         definition: bool = False):
        parent = node.parent

        while parent.name != cls.GLOBAL_SCOPE_NODE:
            parent = parent.parent

        if parent.scope is None:
            parent.set_scope(Scope())

        parent.scope.append({
            'identifier': identifier,
            'parameter_types': parameter_types,
            'return_type': return_type,
            'kind': 'function',
            'definition': definition
        })
