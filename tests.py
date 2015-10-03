import unittest

from parsing import (
    ParseError,
    Take, TakeIf, TakeWhile,
)


class TestTake(unittest.TestCase):
    def test_it_should_parse_the_given_number_of_characters(self):
        p = Take(3)

        self.assertEqual(p.parse('arst'), ('ars', 't'))

    def test_it_should_require_a_number_greater_than_zero(self):
        with self.assertRaises(ValueError):
            Take(0)

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ParseError):
            Take(10).parse('arst')


class TestTakeIf(unittest.TestCase):
    def test_it_should_conditionally_parse_the_given_number_of_characters(self):
        p = TakeIf(3, lambda x: x.isalpha())

        self.assertEqual(p.parse('arst'), ('ars', 't'))

    def test_it_should_require_a_number_greater_than_zero(self):
        with self.assertRaises(ValueError):
            TakeIf(0, lambda x: None)

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        p = TakeIf(3, lambda x: x.isalpha())

        with self.assertRaises(ParseError):
            p.parse('ar12')


class TestTakeWhile(unittest.TestCase):
    def test_it_should_parse_input_as_long_as_the_predicate_is_true(self):
        p = TakeWhile(lambda x: x.isalpha())

        self.assertEqual(p.parse('ars1'), ('ars', '1'))


if __name__ == '__main__':
    unittest.main()
