import unittest

from parsing import (
    NotEnoughInputError, ConditionNotMetError,
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
        with self.assertRaises(NotEnoughInputError):
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

        with self.assertRaises(ConditionNotMetError):
            p.parse('ar12')

        with self.assertRaises(NotEnoughInputError):
            p.parse('ar')


class TestTakeWhile(unittest.TestCase):
    def test_it_should_parse_input_as_long_as_the_predicate_is_true(self):
        p = TakeWhile(lambda x: x.isalpha())

        self.assertEqual(p.parse('ars1'), ('ars', '1'))
        self.assertEqual(p.parse('arst'), ('arst', ''))

    def test_it_should_raise_an_error_under_certain_conditions(self):
        p = TakeWhile(lambda x: x.isalpha())

        # If no characters could be successfully parsed from a non-empty input
        with self.assertRaises(ConditionNotMetError):
            p.parse('1234')

        # If given input is empty
        with self.assertRaises(NotEnoughInputError):
            p.parse('')


if __name__ == '__main__':
    unittest.main()
