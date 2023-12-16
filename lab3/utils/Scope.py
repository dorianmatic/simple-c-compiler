from lab3.utils.Node import Node


class Scope:
    GLOBAL_SCOPE_NODE = '<prijevodna_jedinica>'
    LOCAL_SCOPE_NODE = '<slozena_naredba>'

    def __init__(self):
        self.definitions = []

    def get_definition_identifiers(self):
        return list(map(lambda x: x['identifier'], self.definitions))


    def define_function(self, node: Node, *params):
        pass

    @staticmethod
    def is_declared(node: Node, identifier: str, max_levels=-1):
        levels = 0
        while True:
            current_node = node.parent
            if current_node is None or levels == max_levels:
                return False
            if current_node.scope is None:
                continue
            elif identifier in current_node.scope.get_definition_identifiers():
                return True
            else:
                levels += 1

    @classmethod
    def declare_variable(cls, node: Node, identifier: str, variable_type: str):
        parent = node.parent

        while parent.name != cls.GLOBAL_SCOPE_NODE and parent.name != cls.LOCAL_SCOPE_NODE:
            parent = parent.parent

        if parent.scope is None:
            parent.set_scope(Scope())

        parent.scope.defintions.append({
            'identifier': identifier,
            'type': variable_type
        })