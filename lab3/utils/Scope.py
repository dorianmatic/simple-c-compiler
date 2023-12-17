class Scope:
    LOCAL_SCOPE_NODE = '<slozena_naredba>'

    def __init__(self):
        self.declarations = []

    def add_declaration(self, declaration_params):
        self.declarations.append(declaration_params)
