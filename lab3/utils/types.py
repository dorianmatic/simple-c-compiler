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

    @staticmethod
    def validate_int(value):
        return -2147483648 <= value <= 2147483647

    @staticmethod
    def validate_char(value):
        # TODO: Finish char validation implementation
        return 0 <= value <= 255