def find_closing_parent(string):
    n = 0
    for i, c in enumerate(string):
        if c == ')':
            if n == 1:
                return i
            else:
                n -= 1
        elif c == '(':
            n += 1

    return -1


def process_escaped_symbols(regex):
    specials = [('\\n', '\n'), ('\\t', '\t'), ('\\_', ' '), ('\\)', ')'), ('\\(', '('), ('\\|', '|'),
                ('\\*', '*'), ('\\$', '$'), ('\\}', '}'), ('\\{', '{')]

    for s in specials:
        regex = regex.replace(*s)

    return regex