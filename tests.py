import unittest

from parsing import ParsingError, Take


class TestTake(unittest.TestCase):
    def setUp(self):
        self.s = 'arst'

    def test_it_should_parse_the_given_number_of_characters(self):
        p = Take(3)

        self.assertEqual(p.parse(self.s), ('ars', 't'))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        p = Take(10)

        with self.assertRaises(ParsingError):
            self.assertEqual(p.parse(self.s), ('ars', 't'))


if __name__ == '__main__':
    unittest.main()
