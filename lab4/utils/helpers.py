def is_non_terminal(symbol):
    """
    Check if a symbol is non-terminal. I.e. starts with '<' and ends with '>'
    """

    return symbol.startswith('<') and symbol.endswith('>')