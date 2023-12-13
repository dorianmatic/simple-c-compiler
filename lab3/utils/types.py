class Types:
    CHAR = 'char'
    INT = 'int'
    CONST_CHAR = 'const(char)'
    CONST_INT = 'const(int)'
    ARRAY_CHAR = 'niz(char)'
    ARRAY_INT = 'niz(char)'
    ARRAY_CONST_CHAR = 'niz(const(char))'
    ARRAY_CONST_INT = 'niz(const(int))'
    VOID = 'void'

    CASTS = [
        (CONST_INT, INT), (INT, CONST_INT),
        (CONST_CHAR, CHAR), (CHAR, CONST_CHAR),
        (CHAR, INT), (CHAR, CONST_INT),
        (CONST_CHAR, INT), (CONST_CHAR, CONST_INT),
        (ARRAY_INT, ARRAY_CONST_INT), (ARRAY_CHAR, ARRAY_CONST_CHAR)
    ]

    # TODO: Can one cast to CONST_INT?
    EXPLICIT_CASTS = [
        (CHAR, INT), (CONST_CHAR, INT)
    ]


    @staticmethod
    def validate_int(value):
        return -2147483648 <= value <= 2147483647

    @staticmethod
    def validate_char(value):
        # TODO: Finish char validation implementation
        return 0 <= value <= 255

    @staticmethod
    def validate_string(value):
        pass

    @classmethod
    def is_castable(cls, from_type, to_type):
        return (from_type, to_type) in cls.CASTS

    @classmethod
    def is_explicitly_castable(cls, from_type, to_type):
        return (from_type, to_type) in cls.EXPLICIT_CASTS

    @classmethod
    def is_array(cls, var_type):
        return 'niz' in var_type

    @classmethod
    def get_array_type(cls, var_type):
        return var_type[4:-1]

    @classmethod
    def is_const(cls, var_type):
        return 'const' in var_type

    @staticmethod
    def to_const(var_type):
        return f'const({var_type})'

    @staticmethod
    def to_array(var_type):
        return f'niz({var_type})'