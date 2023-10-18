import re


def regular_definition_to_expression(definition, regular_definitions):
    """
    Converts the regular definition into a regular expression. Also, resolves all the other definition the given
    definition might reference.
    """

    while match := re.search(r'\{[a-z|A-Z]*?\}', definition):
        exp_before = definition[:match.span()[0]]
        exp_after = definition[match.span()[1]:]
        other_exp = regular_definitions[match.group()]

        definition = exp_before + f'({other_exp})' + exp_after

    return definition


def escaped(regex, position):
    """Checks if the symbol in a given position in the regex is escaped by '\' or not."""

    backslash_n = 0
    for i in range(position-1, -1, -1):
        if regex[i] != '\\':
            break

        backslash_n += 1

    return backslash_n % 2 == 1


def split_by_or(regex):
    """Splits the regex by top-level pipes - '|'."""

    parentheses = 0
    or_choices = []
    prev_choice = 0

    for i, c in enumerate(regex):
        if escaped(regex, i):
            continue

        if c == '(':
            parentheses += 1
        elif c == ')':
            parentheses -= 1
        elif c == '|' and parentheses == 0:
            or_choices.append(regex[prev_choice:i])
            prev_choice = i + 1

    if len(or_choices) != 0 and regex[prev_choice:]:
        or_choices.append(regex[prev_choice:])

    return or_choices
