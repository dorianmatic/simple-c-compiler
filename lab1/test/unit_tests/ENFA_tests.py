from lab1.utils.ENFA import ENFA
import unittest


class TestENFA(unittest.TestCase):
    def test_string_validation_1(self):
        enfa = ENFA(regex='(a|b)*')

        self.assertEqual(enfa.validate('aabbaba'), 'match')
        self.assertEqual(enfa.validate('abc'), 'no-match')

    def test_string_validation_2(self):
        enfa = ENFA(regex='c|(aa)*')

        self.assertEqual(enfa.validate('c'), 'match')
        self.assertEqual(enfa.validate('aa'), 'match')

        self.assertEqual(enfa.validate('aaa'), 'potential')

        self.assertEqual(enfa.validate('cc'), 'no-match')
        self.assertEqual(enfa.validate('ca'), 'no-match')

    def test_string_validation_3(self):
        enfa = ENFA(regex='abc((ef)*|gh)')

        self.assertEqual(enfa.validate('abc'), 'match')
        self.assertEqual(enfa.validate('abcefef'), 'match')
        self.assertEqual(enfa.validate('abcgh'), 'match')

        self.assertEqual(enfa.validate('abce'), 'potential')

        self.assertEqual(enfa.validate('efef'), 'no-match')
        self.assertEqual(enfa.validate('gh'), 'no-match')
        self.assertEqual(enfa.validate('efgh'), 'no-match')

    def test_string_validation_4(self):
        enfa = ENFA(regex='o(ab|bc|ca)*')

        self.assertEqual(enfa.validate('oabbcca'), 'match')
        self.assertEqual(enfa.validate('ocacaca'), 'match')
        self.assertEqual(enfa.validate('oa'), 'potential')


if __name__ == '__main__':
    unittest.main()
