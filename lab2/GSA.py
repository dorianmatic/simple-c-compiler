import fileinput
import pickle
from pathlib import Path

from lab2.utils.DFA import *
from lab2.utils.ENFA import ENFA
from lab2.utils.LRParser import LRParser


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


def prepare_pickle(terminals, non_terminals, syncs, parser):
    return {
        'non_terminals': non_terminals,
        'sync_non_terminals': syncs,
        'terminals': terminals,
        'parser_actions': parser.actions,
        'parser_new_states': parser.new_states
    }


def add_starting_production(nonterminals, productions):
    """Adding an artificial starting nonterminal and starting production per instructions on pg. 31"""
    starting_nonterminal = "<S0>"
    production = {"left": starting_nonterminal, "right": [nonterminals[0]]}
    nonterminals.insert(0, starting_nonterminal)
    productions.insert(0, production)
    return nonterminals, productions


if __name__ == "__main__":
    productions = []
    non_terminals = []
    terminals = []
    sync_non_terminals = []

    left = ""
    production = create_empty_production()
    production_processing = False
    for line in fileinput.input():
        line_type = identify_line(line)

        if line_type == LineTypes.NONTERMINAL:
            non_terminals = process_symbols(line)
        elif line_type == LineTypes.TERMINAL:
            terminals = process_symbols(line)
        elif line_type == LineTypes.SYN:
            sync_non_terminals = process_symbols(line)
        elif line_type == LineTypes.PRODUCTION:
            production, left, newLeftSymbol = process_production_line(
                production, line, left
            )
            if not newLeftSymbol:
                productions.append(production)
            production = create_empty_production()

    non_terminals, productions = add_starting_production(non_terminals, productions)
    enfa = ENFA.from_context_free_grammar(productions, terminals, non_terminals)
    enfa.to_nka()

    dfa = DFA.from_nka(enfa)
    # print(*productions, sep='\n')
    parser = LRParser.from_dfa(dfa, productions)

    pickle.dump(prepare_pickle(terminals, non_terminals, sync_non_terminals, parser),
                Path(__file__).parent.joinpath('analizator', 'SA_data.pkl').open('wb'))

