import itertools


def find_class(el, coll):
    for i, sub in enumerate(coll):
        if el in sub:
            return i
    return -1


class DFMachine:
    class Transition:
        def __init__(self, old, new, symbol):
            self.old = old
            self.new = new
            self.symbol = symbol

    class State:
        def __init__(self, name, acceptable):
            self.name = name
            self.active = False
            self.acceptable = acceptable

        def set_active(self, active):
            self.active = active

        def __eq__(self, other):
            return self.name == other.name

        def __hash__(self):
            return hash(repr(self))

        def __str__(self):
            return self.name

        def __lt__(self, other):
            return self.name < other.name

    def __init__(self, transitions, active, symbols, acceptable):
        self.states = []
        self.transitions = []
        self.symbols = symbols
        self.acceptable = acceptable

        for t in transitions:
            self._add_transition(*t)

        self._find_or_create_state(active).set_active(True)

    def simplify(self):
        unreachable = self._find_unreachable()
        # keep only the reachable states and their transitions
        self.transitions = list(filter(lambda t: t.old not in unreachable and t.new not in unreachable,
                                       self.transitions))
        self.states = list(filter(lambda s: s not in unreachable, self.states))

        equivalent = self._find_equivalent()
        for m, eq in equivalent.items():
            # remove all transitions that start in equivalent state
            self.transitions = list(filter(lambda t: t.old not in eq, self.transitions))
            # those that end in equivalent states should end in one state
            for t in filter(lambda t: t.new in eq, self.transitions):
                t.new = m

            if True in map(lambda x: x.active, eq):
                m.set_active(True)

            self.states = list(filter(lambda s: s not in eq, self.states))

    def print(self):
        print(','.join(sorted(map(lambda s: s.name, self.states))))
        print(','.join(self.symbols))
        print(','.join(sorted(map(lambda s: s.name, filter(lambda s: s.acceptable, self.states)))))
        print(next(self._get_active()).name)
        for t in self.transitions:
            print(f'{t.old},{t.symbol}->{t.new}')

    # Private

    def _find_equivalent(self):
        acc = sorted(filter(lambda x: x.acceptable, self.states))
        non_acc = sorted(filter(lambda x: not x.acceptable, self.states))
        division = [non_acc, acc]

        while True:
            new_division = []
            for div in division:
                new_division.extend(list(map(lambda x: list(x[1]),
                                             itertools.groupby(div, lambda x: self._grouper(x, division)))))

            if division == new_division:
                break

            division = new_division

        equivalent = {}
        for div in division:
            equivalent[div[0]] = div[1:]

        return equivalent

    def _grouper(self, state, division):
        return list(map(lambda s: find_class(self._find_transition_new_state(state, s), division), self.symbols))

    def _find_transition_new_state(self, state, symbol):
        if transition := next(filter(lambda t: t.old == state and t.symbol == symbol, self.transitions)):
            return transition.new
        else:
            return None

    def _find_unreachable(self):
        reachable = {next(self._get_active())}
        new_states = {next(self._get_active())}

        while True:
            temp = set()
            for q in new_states:
                temp = temp | set(map(lambda s: s.new, filter(lambda t: t.old == q, self.transitions)))

            new_states = temp - reachable

            if len(new_states) == 0:
                break

            reachable = reachable | new_states

        return set(self.states) - reachable

    def _add_transition(self, old, symbol, new):
        if new == '#':
            return

        old_state = self._find_or_create_state(old)
        new_state = self._find_or_create_state(new)

        self.transitions.append(self.Transition(old_state, new_state, symbol))

    def _find_or_create_state(self, name):
        if state := next(filter(lambda x: x.name == name, self.states), None):
            return state

        self.states.append(self.State(name, name in self.acceptable))

        return self.states[-1]

    def _get_active(self):
        return filter(lambda x: x.active, self.states)


states = input().split(',')
symbols = input().split(',')
acceptable = input().split(',')
active = input()

transitions = []
try:
    while transition_raw := input():
        transition_raw = transition_raw.split('->')
        transition_raw = [transition_raw[0], transition_raw[1].split(',')]
        transition_raw = [f'{transition_raw[0]},{e}' for e in transition_raw[1]]
        transition_raw = map(lambda x: x.split(','), transition_raw)

        transitions.extend(transition_raw)
except EOFError as e:
    pass

m = DFMachine(transitions, active, symbols, acceptable)
m.simplify()

m.print()
