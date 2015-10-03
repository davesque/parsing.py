import unittest

from parsing import (
    NotEnoughInputError, ImproperInputError, Take, TakeIf, TakeWhile, digits,
    alphas, spaces, TakeUntil, Token, word, positive_integer, Accept, All,
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
    def setUp(self):
        self.p = TakeIf(3, lambda x: x.isalpha())

    def test_it_should_conditionally_parse_the_given_number_of_characters(self):
        self.assertEqual(self.p('arst'), ('ars', 't'))

    def test_it_should_be_invertible(self):
        p = ~self.p

        self.assertEqual(p('1234'), ('123', '4'))

    def test_it_should_require_a_number_greater_than_zero(self):
        with self.assertRaises(ValueError):
            TakeIf(0, lambda x: None)

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p('ar12')

        with self.assertRaises(NotEnoughInputError):
            self.p('ar')


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


class TestDigit(unittest.TestCase):
    def test_it_should_parse_input_chars_which_are_digits(self):
        self.assertEqual(digits('1234arst'), ('1234', 'arst'))


class TestAlpha(unittest.TestCase):
    def test_it_should_parse_input_which_is_alphabetical(self):
        self.assertEqual(alphas('arst1234'), ('arst', '1234'))


class TestSpace(unittest.TestCase):
    def test_it_should_parse_input_which_is_whitespace(self):
        self.assertEqual(spaces(' \t\n\rarst'), (' \t\n\r', 'arst'))


class TestToken(unittest.TestCase):
    def test_it_should_parse_using_the_given_parser_and_consume_whitespace(self):
        p = Token(alphas)

        self.assertEqual(p('arst arst'), ('arst', 'arst'))
        self.assertEqual(p('arst '), ('arst', ''))
        self.assertEqual(p('arst'), ('arst', ''))


class TestWord(unittest.TestCase):
    def test_it_should_parse_alphabetical_chars_and_consume_whitespace(self):
        self.assertEqual(word('arst arst'), ('arst', 'arst'))
        self.assertEqual(word('arst '), ('arst', ''))
        self.assertEqual(word('arst'), ('arst', ''))


class TestPositiveInteger(unittest.TestCase):
    def test_it_should_parse_digits_and_return_a_number(self):
        self.assertEqual(positive_integer('1234 arst'), (1234, ' arst'))


class TestAccept(unittest.TestCase):
    def test_it_should_parse_a_specific_string_from_the_front_of_the_input(self):
        p = Accept('arst')

        self.assertEqual(p('arst1234'), ('arst', '1234'))

    def test_it_should_raise_an_error_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            Accept('arst').parse('ars1234')


class TestAll(unittest.TestCase):
    def setUp(self):
        self.p = All(
            word,
            Token(Accept('=')),
            Token(positive_integer),
        )

    def test_it_should_parse_combine_parsers_to_make_a_larger_parser(self):
        self.assertEqual(self.p('arst = 1234'), (('arst', '=', 1234), ''))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p('arst = ')


if __name__ == '__main__':
    unittest.main()
