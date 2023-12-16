class Scope:
    GLOBAL_SCOPE_NODE = '<prijevodna_jedinica>'
    LOCAL_SCOPE_NODE = '<slozena_naredba>'

    def __init__(self):
        self.declarations = []

    def add_declaration(self, declaration_params):
        self.declarations.append(declaration_params)
