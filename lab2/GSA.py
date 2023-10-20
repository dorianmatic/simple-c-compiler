import sys
import fileinput
from pathlib import Path
import pickle


class LineTypes:
    """ Enum for different line types."""

    TERMINAL = 'terminal '
    NONTERMINAL = 'non-terminal'
    SYN = 'syn'
    PRODUCTION = 'production'


def identify_line(line):
    """ Identify the current line. """

    if line.startswith('<') or line.startswith(' '):
        return LineTypes.PRODUCTION
    if line.startswith('%Syn'):
        return LineTypes.SYN
    if line.startswith('%V'):
        return LineTypes.NONTERMINAL
    if line.startswith('%T'):
        return LineTypes.TERMINAL

    return None



def process_symbols(symbols):
    return symbols.strip().split(' ')[1:]


def process_production_line(production, production_line, left):
    """ A function which adds production rules to the production list.
    """
    if production_line.startswith('<'):
        newLeftSymbol = True
        left = production_line.strip()
    elif production_line.startswith(' '):
        newLeftSymbol = False
        right = production_line.strip().split(' ')
        production['left']=left
        production['right']=right

    return production, left, newLeftSymbol


def create_empty_production():
    return {'left': '', 'right': []}


if __name__ == '__main__':
    productions = []
    left = ''
    production = create_empty_production()
    production_processing = False
    for line in fileinput.input():
        line_type = identify_line(line)

        if line_type == LineTypes.NONTERMINAL:
            nonterminals = process_symbols(line)
        elif line_type == LineTypes.TERMINAL:
            terminals = process_symbols(line)
        elif line_type == LineTypes.SYN:
            sync_nonterminals = process_symbols(line)
            pass
        elif line_type == LineTypes.PRODUCTION:
            production, left, newLeftSymbol = process_production_line(production, line, left)
            if not newLeftSymbol:
                productions.append(production)
            production = create_empty_production()


    # Note: this only works for Python 3.9+
    # rules = map(lambda rule: rule | {'regex': regular_definition_to_expression(rule['regex'], regular_definitions)},
    #             rules)
    # rules = map(lambda rule: rule | {'nfa_definition': ENFA(regex=rule['regex']).export_definition()},
    #             rules)

    # LA_definition = {
    #     'init_state': states[0],
    #     'rules': list(rules)
    # }

    # pickle.dump(LA_definition, Path(__file__).parent.joinpath('analizator', 'SA_data.pkl').open('wb'))
