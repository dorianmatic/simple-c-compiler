class Zapocinje:
    """Contains all methods needed to calculate the Zapocinje set of characters"""

    def __init__(self, productions, terminals, nonterminals):
        self.productions = productions
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.empty_nonterminals = self.find_empty_nonterminals(self.productions, [])
        self.matrix = self.starts_with_matrix(self.starts_with_instant_matrix())

    def initialize_matrix(self, shape):
        matrix = []
        for i in range(shape):
            row = [0] * shape
            matrix.append(row)
        for i in range(shape):
            matrix[i][i] = -1
        return matrix

    def find_empty_nonterminals(self, productions, empty_nonterminals):
        """Returns a list of empty nonterminals"""
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
                if empty == True:
                    empty_nonterminals.append(production["left"])
                    added = True
        if added == True:
            filter_productions = [
                production
                for production in self.productions
                if production["left"] not in empty_nonterminals
            ]
            return self.find_empty_nonterminals(filter_productions, empty_nonterminals)
        return empty_nonterminals

    def generate_empty(self, characters):
        """Returns True if it is possible to generate an empty char from the characters else False"""
        for char in characters:
            if char not in self.empty_nonterminals:
                return False
        return True

    def starts_with_instant_matrix(self):
        row = self.nonterminals + self.terminals
        matrix = self.initialize_matrix(len(row))
        for production in self.productions:
            left = production["left"]
            right = production["right"]
            index_row = row.index(left)
            if right[0] != "$":
                for sign in right:
                    index_col = row.index(sign)
                    matrix[index_row][index_col] = 1
                    if sign not in self.empty_nonterminals:
                        break

        return matrix

    def starts_with_matrix(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i][j] == 1:
                    for k in range(len(matrix)):
                        if matrix[j][k]:
                            matrix[i][k] = -1

        return matrix

    def starts_with(self, character):
        start = []
        index_row = self.nonterminals.index(character)
        char_row = self.matrix[index_row]
        for i in range(len(self.nonterminals), len(char_row)):
            if char_row[i] == 1 or char_row[i] == -1:
                start.append(self.terminals[i - len(self.nonterminals)])
        return start

    def start_union(self, characters):
        starting_terminals = set()
        if characters[0] != "$":
            for char in characters:
                if not char.startswith("<"):
                    starting_terminals.add(char)
                    break
                else:
                    starting_terminals.update(self.starts_with(char))
                    if char not in self.empty_nonterminals:
                        break

        return list(starting_terminals)
