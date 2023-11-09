from lab2.utils.LRParser import LRParser, ActionsEnum
import unittest

actions = [
        {
            'var': { 'type': ActionsEnum.MOVE, 'new_state': 5 }, '(': { 'type': ActionsEnum.MOVE, 'new_state': 4 }
        },
        {
            '+': { 'type': ActionsEnum.MOVE, 'new_state': 6}, '$': {'type': ActionsEnum.ACCEPT }
        },
        {
            '+': { 'type': ActionsEnum.REDUCE, 'left': 'E', 'right': ['T'] },
            '*': { 'type': ActionsEnum.MOVE, 'new_state': 7 },
            ')': { 'type': ActionsEnum.REDUCE, 'left': 'E', 'right': ['T'] },
            '$': { 'type': ActionsEnum.REDUCE, 'left': 'E', 'right': ['T'] }},
        {
            '+': { 'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['F'] },
            '*': { 'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['F'] },
            ')': { 'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['F'] },
            '$': { 'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['F'] }
        },
        {
            'var': { 'type': ActionsEnum.MOVE, 'new_state': 5 }, '(': { 'type': ActionsEnum.MOVE, 'new_state': 4 }
        },
        {
            '+': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['var']},
            '*': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['var']},
            ')': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['var']},
            '$': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['var']}
        },
        {
            'var': {'type': ActionsEnum.MOVE, 'new_state': 5}, '(': {'type': ActionsEnum.MOVE, 'new_state': 4}
        },
        {
            'var': {'type': ActionsEnum.MOVE, 'new_state': 5}, '(': {'type': ActionsEnum.MOVE, 'new_state': 4}
        },
        {
            '+': {'type': ActionsEnum.MOVE, 'new_state': 6}, ')': {'type': ActionsEnum.MOVE, 'new_state': 11}
        },
        {
            '+': {'type': ActionsEnum.REDUCE, 'left': 'E', 'right': ['E', '+', 'T']},
            '*': {'type': ActionsEnum.MOVE, 'new_state': 7},
            ')': {'type': ActionsEnum.REDUCE, 'left': 'E', 'right': ['E', '+', 'T']},
            '$': {'type': ActionsEnum.REDUCE, 'left': 'E', 'right': ['E', '+', 'T']}
        },
        {
            '+': {'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['T', '*', 'F']},
            '*': {'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['T', '*', 'F']},
            ')': {'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['T', '*', 'F']},
            '$': {'type': ActionsEnum.REDUCE, 'left': 'T', 'right': ['T', '*', 'F']}
        },
        {
            '+': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['(', 'E', ')']},
            '*': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['(', 'E', ')']},
            ')': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['(', 'E', ')']},
            '$': {'type': ActionsEnum.REDUCE, 'left': 'F', 'right': ['(', 'E', ')']}
        },
    ]
new_states = [
        {'E': 1, 'T': 2, 'F': 3},
        {},
        {},
        {},
        {'E': 8, 'T': 2, 'F': 3},
        {},
        {'T': 9, 'F': 3},
        {'F': 10},
        {}, {}, {}, {}
    ]

class LRParserTest(unittest.TestCase):
    def test_parser(self):
        parser = LRParser(actions=actions, new_states=new_states, sequence=['var', '+', 'var', '*', 'var'])

        self.assertTrue(parser.parse())

        parser.init_stack()
        parser.set_sequence(['var', '+', 'var', '*', 'var', '+', 'var'])
        self.assertTrue(parser.parse())

        parser.init_stack()
        parser.set_sequence(['(', 'var' , ')', '*', 'var', '+', '(', 'var', '+', 'var', ')'])
        self.assertTrue(parser.parse())

        parser.init_stack()
        parser.set_sequence(['var', '+', 'var', '*', 'var', '+', '*'])
        self.assertFalse(parser.parse())

    def test_tree(self):
        tree = """E
 T
  F
   var
  *
  T
   F
    var
 +
 E
  T
   F
    var"""

        parser = LRParser(actions=actions, new_states=new_states, sequence=['var', '+', 'var', '*', 'var'])
        parser.parse()
        self.assertEqual(parser.get_tree(), tree)