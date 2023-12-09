from lab2.utils.helpers import *

class StartsUtils:
    """Contains all methods needed to calculate the FIRST sets."""

    def __init__(self, productions, terminals, non_terminals):
        self.productions = productions
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.empty_non_terminals = self.find_empty_non_terminals(self.productions, [])
        self.starts_with_dict = {}

    def starts_with(self, non_terminal):
        """
        Returns any possible symbol a sequence generate from non_terminal can start with.

        :param non_terminal:
        :param productions:
        :return:
        """

        possible_first_symbols = []
        queue = list(filter(lambda x: x['left'] == non_terminal, self.productions))
        visited = list(queue)
        while queue:
            production = queue.pop(0)
            for c in production['right']:
                if c not in possible_first_symbols:
                    possible_first_symbols.append(c)
                    new_list = list(filter(lambda x:x['left']==c,self.productions))
                    new_queue_el = [x for x in new_list if x not in visited]
                    queue.extend(new_queue_el)
                    visited.extend(new_queue_el)
                if c not in self.empty_non_terminals or c in self.terminals:
                    break
        possible_first_symbols = [x for x in possible_first_symbols if x in self.terminals]
        self.starts_with_dict[non_terminal]=possible_first_symbols
        return possible_first_symbols

    def find_empty_non_terminals(self, productions, empty_nonterminals):
        """Returns a list of empty non-terminals"""

        empty_right = ["$"]
        added = False
        for production in productions:
            if production["right"] == empty_right:
                empty_nonterminals.append(production["left"])
                added = True
            else:
                empty = True
                for nt in production["right"]:
                    if nt not in empty_nonterminals:
                        empty = False
                if empty:
                    empty_nonterminals.append(production["left"])
                    added = True
        if added:
            filter_productions = [
                production
                for production in self.productions
                if production["left"] not in empty_nonterminals
            ]
            return self.find_empty_non_terminals(filter_productions, empty_nonterminals)
        return empty_nonterminals

    def generate_empty(self, characters):
        """Returns True if it is possible to generate an empty char from the characters else False"""

        for char in characters:
            if char not in self.empty_non_terminals:
                return False
        return True

    def starts_set_for_sequence(self, sequence):
        """
        Returns the STARTS set for a given sequence.

        :param sequence:
        :return:
        """

        starting_terminals = set()
        if sequence[0] != "$":
            for symbol in sequence:
                if is_non_terminal(symbol):
                    update = self.starts_with_dict.get(symbol, self.starts_with(symbol))
                    starting_terminals.update(update)
                    if symbol not in self.empty_non_terminals:
                        break
                else:
                    starting_terminals.add(symbol)
                    break

        return list(starting_terminals)
