import string

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
    FUNCTION = lambda parameter_types, return_type: {'parameter_types': parameter_types, 'return_type': return_type}

    CASTS = [
        (CONST_INT, INT), (INT, CONST_INT),
        (CONST_CHAR, CHAR), (CHAR, CONST_CHAR),
        (CHAR, INT), (CHAR, CONST_INT),
        (CONST_CHAR, INT), (CONST_CHAR, CONST_INT),
        (ARRAY_INT, ARRAY_CONST_INT), (ARRAY_CHAR, ARRAY_CONST_CHAR)
    ]

    EXPLICIT_CASTS = [
        (CHAR, INT), (INT, CHAR),
        (CONST_CHAR, INT), (INT, CONST_CHAR),
        (INT, CONST_INT), (CONST_INT, INT),
        (CHAR, CONST_CHAR), (CONST_CHAR, CHAR),
        (CONST_CHAR, CONST_INT), (CONST_INT, CONST_CHAR)
    ]

    @staticmethod
    def validate_int(value):
        return -2147483648 <= int(value) <= 2147483647

    @staticmethod
    def validate_char(value):
        return 0 <= ord(value) <= 255

    @staticmethod
    def validate_string(value):
        for i, char in enumerate(value):
            if char == '\\':
                if value[i+1] in ('0', 'n', "'", '"', '\\'):
                    continue
                else:
                    return False
            elif char not in string.printable + '\0':
                return False

        return True

    @classmethod
    def is_castable(cls, from_type, to_type):
        return from_type == to_type or (from_type, to_type) in cls.CASTS

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
