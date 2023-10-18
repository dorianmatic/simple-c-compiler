import sys
from pathlib import Path
import pickle
from utils.ENFA import ENFA
from utils.regex import regular_definition_to_expression


class LineTypes:
    """ Enum for different line types."""

    DEFINITION = 'definition'
    STATES = 'states'
    LEX_UNITS = 'lex units'
    RULE = 'rule'


def identify_line(line, in_rule):
    """ Identify the current line, if rule loading is in progress - return RULE."""

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


def process_rule_line(rule, rule_line):
    """ This function identifies what part of a rule is currently being loaded (action or regex) and act's accordingly.
    """

    rule_loaded = False
    if rule_line.startswith('<'):
        s = rule_line.index('>')

        rule['state'] = rule_line[:s][1:]
        rule['regex'] = rule_line[s+1:]
    elif rule_line.startswith('}'):
        rule_loaded = True
    elif rule_line != '{':
        rule['actions'].append(rule_line)

    return rule, rule_loaded


def create_empty_rule():
    return {'state': '', 'regex': '', 'actions': []}


if __name__ == '__main__':
    regular_definitions = {}
    states = []
    rules = []

    rule = create_empty_rule()
    rule_processing = False

    for line in sys.stdin:
        line = line.strip()
        line_type = identify_line(line, rule_processing)

        if line_type == LineTypes.DEFINITION:
            regular_definitions.update(process_regular_definition(line))
        elif line_type == LineTypes.STATES:
            states = process_states(line)
        elif line_type == LineTypes.LEX_UNITS:
            # We don't care which lexical units are there
            pass
        elif line_type == LineTypes.RULE:
            rule, processed = process_rule_line(rule, line)
            if processed:
                rules.append(rule)
                rule = create_empty_rule()

            rule_processing = not processed

    # Note: this only works for Python 3.9+
    rules = map(lambda rule: rule | {'regex': regular_definition_to_expression(rule['regex'], regular_definitions)},
                rules)
    rules = map(lambda rule: rule | {'nfa_definition': ENFA(regex=rule['regex']).export_definition()},
                rules)

    LA_definition = {
        'init_state': states[0],
        'rules': list(rules)
    }

    pickle.dump(LA_definition, Path(__file__).parent.joinpath('analizator', 'LA_data.pkl').open('wb'))
