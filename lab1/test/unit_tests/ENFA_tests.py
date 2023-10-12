from lab1.utils.ENFA import ENFA
import unittest


class TestENFA(unittest.TestCase):
    def test_string_validation_1(self):
        enfa = ENFA(regex='(a|b)*')

        self.assertTrue(enfa.validate('aabbaba'))
        self.assertFalse(enfa.validate('abc'))

    def test_string_validation_2(self):
        enfa = ENFA(regex='c|(aa)*')

        self.assertTrue(enfa.validate('c'))
        self.assertTrue(enfa.validate('aa'))

        self.assertFalse(enfa.validate('cc'))
        self.assertFalse(enfa.validate('aaa'))
        self.assertFalse(enfa.validate('ca'))

    def test_string_validation_3(self):
        enfa = ENFA(regex='abc((ef)*|gh)')

        self.assertTrue(enfa.validate('abc'))
        self.assertTrue(enfa.validate('abcefef'))
        self.assertTrue(enfa.validate('abcgh'))

        self.assertFalse(enfa.validate('efef'))
        self.assertFalse(enfa.validate('gh'))
        self.assertFalse(enfa.validate('efgh'))

    def test_string_validation_4(self):
        enfa = ENFA(regex='o(ab|bc|ca)*')

        self.assertTrue(enfa.validate('oabbcca'))
        self.assertTrue(enfa.validate('ocacaca'))

    def test_string_validation_5(self):
        enfa = ENFA(regex='\n')

        self.assertTrue(enfa.validate('\n'))
        self.assertFalse(enfa.validate('ocacaca'))


if __name__ == '__main__':
    unittest.main()
