from lab2.utils.helpers import *

class Zapocinje:
    """Contains all methods needed to calculate the Zapocinje set of characters"""

    def __init__(self, productions, terminals, non_terminals):
        self.productions = productions
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.empty_non_terminals = self.find_empty_non_terminals(productions)
        self.matrix = self.initialize_matrix()
        self.mark_starts_directly_matrix()
        self.mark_transitive_matrix()

    def mark_starts_directly_matrix(self):
        """
        Apply starts_directly_with for every non-terminal.

        :param matrix:
        :return:
        """
        for non_terminal in self.non_terminals:
            possible_first_symbols = self.starts_directly_with(non_terminal, self.productions)
            for symbol in possible_first_symbols:
                self.matrix[non_terminal][symbol] = 1

    def mark_transitive_matrix(self):
        """
        If matrix[j][k] is marked and matrix[k][l] is marked, matrix[j][l] must be marked.

        :return:
        """

        for j in self.non_terminals:
            for k in self.non_terminals:
                for l in self.non_terminals:
                    if self.matrix[j].get(k) == 1 and self.matrix[k].get(l) == 1:
                        self.matrix[j][l] = 1

    def initialize_matrix(self):
        """
        Initialize the matrix and set '*' on diagonals.
        :return:
        """

        return dict([(symbol, { symbol: 1 }) for symbol in self.non_terminals + self.terminals])

    def starts_directly_with(self, non_terminal, productions):
        """
        Returns any possible symbol a sequence generate from non_terminal can start with.

        :param non_terminal:
        :param productions:
        :return:
        """

        possible_first_symbols = []
        queue = list(filter(lambda x: x['left'] == non_terminal, productions))
        while queue:
            production = queue[0]
            if is_non_terminal(production['right'][0]):
                queue.extend(list(filter(lambda x: x['left'] == production['right'][0], productions)))

            possible_first_symbols.append(production['right'][0])
            queue = queue[1:]

        return possible_first_symbols

    def find_empty_non_terminals(self, productions):
        empty_non_terminals = set(map(lambda x: x['left'], filter(lambda x: x['right'] == [], productions)))

        expanded = True
        while expanded:
            expanded = False
            for production in productions:
                if set(production['right']).difference(empty_non_terminals) == {} and production['left'] not in empty_non_terminals:
                    empty_non_terminals.update(production['left'])
                    expanded = True

        return empty_non_terminals


    def generate_empty(self, sequence):
        """Returns True if it is possible to generate an empty char from the characters else False"""

        return all(map(lambda x: x in self.empty_non_terminals, sequence))

    def starts_set_for_non_terminal(self, non_terminal):
        """
        Returns the STARTS set for a given non-terminal.

        :param non_terminal:
        :return:
        """

        return map(lambda x: x[0],
                    filter(lambda x: x[0] in self.terminals and x[1] == 1, self.matrix[non_terminal].items()))

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
                    starting_terminals.update(self.starts_set_for_non_terminal(symbol))

                    if symbol not in self.empty_non_terminals:
                        break
                else:
                    starting_terminals.add(symbol)
                    break

        return list(starting_terminals)
