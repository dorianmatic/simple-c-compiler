import re
from util.ENFA import ENFA
from util.regex import regular_definition_to_expression

regular_definitions = {}
states = []
lex_units = []
rules = []

regular_expressions = {}


class LineTypes:
    DEFINITION = 'definition'
    STATES = 'states'
    LEX_UNITS = 'lex units'
    RULE = 'rule'


def identify_line(line, in_rule):
    if line.startswith('<') or in_rule:
        return LineTypes.RULE
    if line.startswith('{'):
        return LineTypes.DEFINITION
    if line.startswith('%X'):
        return LineTypes.STATES
    if line.startswith('%L'):
        return LineTypes.LEX_UNITS

    return None


def process_regular_definition(definition):
    definition = definition.split(' ')

    return {definition[0]: definition[1]}


def process_states(states):
    return states.split(' ')[1:]


def process_lex_units(lex_units):
    return lex_units.split(' ')[1:]


def process_rule_line(rule, rule_line):
    rule_loaded = False
    if rule_line.startswith('<'):
        rule_line = rule_line.split('>')

        rule['state'] = rule_line[0][1:]
        rule['regex'] = rule_line[1]
    elif rule_line.startswith('}'):
        rule_loaded = True
    elif rule_line != '{':
        rule['actions'].append(rule_line)

    return rule, rule_loaded


def create_empty_rule():
    return {'state': '', 'regex': '', 'actions': []}


if __name__ == '__main__':
    rule = create_empty_rule()
    rule_processing = False

    while line := input():
        line_type = identify_line(line, rule_processing)

        if line_type == LineTypes.DEFINITION:
            regular_definitions.update(process_regular_definition(line))
        elif line_type == LineTypes.STATES:
            states = process_states(line)
        elif line_type == LineTypes.LEX_UNITS:
            lex_units = process_lex_units(line)
        elif line_type == LineTypes.RULE:
            rule, processed = process_rule_line(rule, line)
            if processed:
                rules.append(rule)
                rule = create_empty_rule()

            rule_processing = not processed

    print(regular_definitions)
    print(states)
    print(lex_units)
    print(rules)

    # Note: this only works for Python 3.9+
    rules = map(lambda rule: rule | {'regex': regular_definition_to_expression(rule['regex'], regular_definitions)},
                rules)

    rules = map(lambda rule: rule | {'nfa_definition': ENFA(regex=rule['regex']).export_definition()}, rules)

    print(list(rules))
