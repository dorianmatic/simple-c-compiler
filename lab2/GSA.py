import fileinput
from lab2.utils.DKA import *


class LineTypes:
    """Enum for different line types."""

    TERMINAL = "terminal "
    NONTERMINAL = "non-terminal"
    SYN = "syn"
    PRODUCTION = "production"


def identify_line(line):
    """Identify the current line."""

    if line.startswith("<") or line.startswith(" "):
        return LineTypes.PRODUCTION
    if line.startswith("%Syn"):
        return LineTypes.SYN
    if line.startswith("%V"):
        return LineTypes.NONTERMINAL
    if line.startswith("%T"):
        return LineTypes.TERMINAL

    return None


def process_symbols(symbols):
    return symbols.strip().split(" ")[1:]


def process_production_line(production, production_line, left):
    """A function which adds production rules to the production list."""
    if production_line.startswith("<"):
        newLeftSymbol = True
        left = production_line.strip()
    elif production_line.startswith(" "):
        newLeftSymbol = False
        right = production_line.strip().split(" ")
        production["left"] = left
        production["right"] = right

    return production, left, newLeftSymbol


def create_empty_production():
    return {"left": "", "right": []}


def add_starting_production(nonterminals, productions):
    """Adding an artificial starting nonterminal and starting production per instructions on pg. 31"""
    starting_nonterminal = "<S0>"
    production = {"left": starting_nonterminal, "right": [nonterminals[0]]}
    nonterminals.insert(0, starting_nonterminal)
    productions.insert(0, production)
    return nonterminals, productions


if __name__ == "__main__":
    productions = []
    left = ""
    production = create_empty_production()
    production_processing = False
    for line in fileinput.input():
        line_type = identify_line(line)

        if line_type == LineTypes.NONTERMINAL:
            # podrazumijeva se da je nonterminals[0]==pocetni nezavrsni znak
            nonterminals = process_symbols(line)
        elif line_type == LineTypes.TERMINAL:
            terminals = process_symbols(line)
        elif line_type == LineTypes.SYN:
            sync_nonterminals = process_symbols(line)
            pass
        elif line_type == LineTypes.PRODUCTION:
            production, left, newLeftSymbol = process_production_line(
                production, line, left
            )
            if not newLeftSymbol:
                productions.append(production)
            production = create_empty_production()

    nonterminals, productions = add_starting_production(nonterminals, productions)
    ENKA_utils = ENKA(productions, terminals, nonterminals)

    enka_transitions,state_with_terminals = ENKA_utils.construct_enka_transitions()
    DKA_utils = DKA(productions, terminals, nonterminals)
    #DKA_utils.enka_to_nka()
    DKA_utils.nka_to_dka()