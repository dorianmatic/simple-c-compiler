class Variable:

    def __init__(self):
        self.var_type = ""
        self.var_name = ""
        self.mem_loc = []
        self.id = 0
        self.var_value = []
        self.scope = None
        self.var_global = False
        self.root_node = None
        self.list = False
        self.string_var = False

    