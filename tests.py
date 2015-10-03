import unittest

from parsing import (
    NotEnoughInputError, ImproperInputError,
    Take, TakeIf, TakeWhile, alpha, space, TakeUntil, Token,
)


class TestTake(unittest.TestCase):
    def test_it_should_parse_the_given_number_of_characters(self):
        p = Take(3)

        self.assertEqual(p('arst'), ('ars', 't'))

    def test_it_should_require_a_number_greater_than_zero(self):
        with self.assertRaises(ValueError):
            Take(0)

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(NotEnoughInputError):
            Take(10).parse('arst')


class TestTakeIf(unittest.TestCase):
    def test_it_should_conditionally_parse_the_given_number_of_characters(self):
        p = TakeIf(3, lambda x: x.isalpha())

        self.assertEqual(p('arst'), ('ars', 't'))

    def test_it_should_require_a_number_greater_than_zero(self):
        with self.assertRaises(ValueError):
            TakeIf(0, lambda x: None)

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        p = TakeIf(3, lambda x: x.isalpha())

        with self.assertRaises(ImproperInputError):
            p('ar12')

        with self.assertRaises(NotEnoughInputError):
            p('ar')


class TestTakeWhile(unittest.TestCase):
    def test_it_should_parse_input_as_long_as_the_predicate_is_true(self):
        p = TakeWhile(lambda x: x.isalpha())

        self.assertEqual(p('ars1'), ('ars', '1'))
        self.assertEqual(p('arst'), ('arst', ''))

    def test_it_should_raise_an_error_under_certain_conditions(self):
        p = TakeWhile(lambda x: x.isalpha())

        # If no characters could be successfully parsed from a non-empty input
        with self.assertRaises(ImproperInputError):
            p('1234')

        # If given input is empty
        with self.assertRaises(NotEnoughInputError):
            p('')


class TestTakeUntil(unittest.TestCase):
    def test_it_should_parse_input_until_an_occurrence_of_the_given_string(self):
        p = TakeUntil('arst')

        self.assertEqual(p('before arst after'), ('before ', 'arst after'))

    def test_it_should_raise_an_error_if_the_given_string_is_not_found(self):
        p = TakeUntil('arst')

        with self.assertRaises(ImproperInputError):
            p('before after')


class TestAlpha(unittest.TestCase):
    def test_it_should_parse_input_which_is_alphabetical(self):
        self.assertEqual(alpha('arst1234'), ('arst', '1234'))


class TestSpace(unittest.TestCase):
    def test_it_should_parse_input_which_is_whitespace(self):
        self.assertEqual(space(' \t\n\rarst'), (' \t\n\r', 'arst'))


class TestToken(unittest.TestCase):
    def test_it_should_parse_using_the_given_parser_and_consume_whitespace(self):
        p = Token(alpha)

        self.assertEqual(p('arst arst'), ('arst', 'arst'))
        self.assertEqual(p('arst '), ('arst', ''))
        self.assertEqual(p('arst'), ('arst', ''))


if __name__ == '__main__':
    unittest.main()
