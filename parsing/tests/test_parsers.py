from __future__ import unicode_literals

import unittest

from ..basic import digits, alphas, spaces, positive_integer
from ..exceptions import NotEnoughInputError, ImproperInputError
from ..parsers import (
    TakeItems, TakeItemsIf, TakeWhile, TakeUntil, Token, TakeIf, TakeAll,
    Apply, Literal, Discardable, Discard, Sequence, Optional, Alternatives,
)
from ..utils import compose, flatten, join, is_alpha, unary, equals


class TestParserBuilding(unittest.TestCase):
    def test_it_should_allow_building_of_parser_with_bitwise_operations(self):
        p1 = alphas & digits
        self.assertEqual(p1.parse_string('arst1234'), (('arst', '1234'), ''))

        p2 = alphas | digits
        self.assertEqual(p2.parse_string('arst1234'), ('arst', '1234'))
        self.assertEqual(p2.parse_string('1234arst'), ('1234', 'arst'))

        p3 = positive_integer | (alphas & (digits | spaces))
        self.assertEqual(
            p3.parse_string('1234arst1234    '),
            (1234, 'arst1234    '),
        )
        self.assertEqual(
            p3.parse_string('arst1234    1234'),
            (('arst', '1234'), '    1234'),
        )
        self.assertEqual(
            p3.parse_string('arst    1234'),
            (('arst', '    '), '1234'),
        )


class TestTakeItems(unittest.TestCase):
    def test_it_should_parse_the_given_number_of_characters(self):
        p = TakeItems(3)

        self.assertEqual(p.parse_string('arst'), ('ars', 't'))

    def test_it_should_require_a_number_greater_than_zero(self):
        with self.assertRaises(ValueError):
            TakeItems(0)

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(NotEnoughInputError):
            TakeItems(10).parse_string('arst')


class TestTakeItemsIf(unittest.TestCase):
    def setUp(self):
        self.p = TakeItemsIf(3, is_alpha)

    def test_it_should_conditionally_parse_the_given_number_of_characters(self):
        self.assertEqual(self.p.parse_string('arst'), ('ars', 't'))

    def test_it_should_be_invertible(self):
        p = ~(self.p)
        self.assertEqual(p.parse_string('1234'), ('123', '4'))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('ar12')


class TestTakeWhile(unittest.TestCase):
    def setUp(self):
        self.p = TakeWhile(is_alpha)

    def test_it_should_parse_input_as_long_as_the_predicate_is_true(self):
        self.assertEqual(self.p.parse_string('ars1'), ('ars', '1'))
        self.assertEqual(self.p.parse_string('arst'), ('arst', ''))

    def test_it_should_raise_an_error_under_certain_conditions(self):
        # If no characters could be successfully parsed from a non-empty input
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('1234')


class TestDigits(unittest.TestCase):
    def test_it_should_parse_input_chars_which_are_digits(self):
        self.assertEqual(digits.parse_string('1234arst'), ('1234', 'arst'))


class TestAlphas(unittest.TestCase):
    def test_it_should_parse_input_which_is_alphabetical(self):
        self.assertEqual(alphas.parse_string('arst1234'), ('arst', '1234'))


class TestSpaces(unittest.TestCase):
    def test_it_should_parse_input_which_is_whitespace(self):
        self.assertEqual(spaces.parse_string(' \t\n\rarst'), (' \t\n\r', 'arst'))


class TestTakeUntil(unittest.TestCase):
    def setUp(self):
        self.p = TakeUntil(Literal('arst'))

    def test_it_should_parse_input_until_the_given_parser_succeeds(self):
        self.assertEqual(self.p.parse_string('before arst after'), ('before ', 'arst after'))

    def test_it_should_accept_a_string_as_an_argument(self):
        # In this case, it should just parse until the literal string is
        # encountered
        self.assertEqual(TakeUntil('arst').parse_string('before arst after'), ('before ', 'arst after'))

    def test_it_should_raise_an_error_if_the_given_parser_never_succeeds(self):
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('before after')

    def test_it_should_raise_an_error_if_the_given_parser_succeeds_immediately(self):
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('arst')


class TestToken(unittest.TestCase):
    def test_it_should_parse_using_the_given_parser_and_consume_whitespace(self):
        p = Token(alphas)

        self.assertEqual(p.parse_string('arst arst'), ('arst', 'arst'))
        self.assertEqual(p.parse_string('arst '), ('arst', ''))
        self.assertEqual(p.parse_string('arst'), ('arst', ''))


class TestTakeIf(unittest.TestCase):
    def setUp(self):
        self.p = TakeIf(Token(alphas), equals('yodude'))

    def test_it_should_parse_input_using_the_given_parser_validated_by_the_given_predicate(self):
        self.assertEqual(self.p.parse_string('yodude arst'), ('yodude', 'arst'))

    def test_it_should_raise_an_error_if_nothing_can_be_parsed(self):
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('arst arst')


class TestTakeAll(unittest.TestCase):
    def setUp(self):
        self.p = TakeAll(Token(alphas))

    def test_it_should_parse_input_using_the_given_parser_until_it_fails(self):
        self.assertEqual(self.p.parse_string('arst arst arst 1234'), (('arst', 'arst', 'arst'), '1234'))

    def test_it_should_raise_an_error_if_nothing_can_be_parsed(self):
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('1234 arst')


class TestPositiveInteger(unittest.TestCase):
    def test_it_should_parse_digits_and_return_a_number(self):
        self.assertEqual(positive_integer.parse_string('1234 arst'), (1234, ' arst'))


class TestLiteral(unittest.TestCase):
    def test_it_should_parse_a_specific_string_from_the_front_of_the_input(self):
        p = Literal('arst')

        self.assertEqual(p.parse_string('arst1234'), ('arst', '1234'))

    def test_it_should_raise_an_error_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            Literal('arst').parse_string('ars1234')


class TestSequence(unittest.TestCase):
    def setUp(self):
        self.p1 = Sequence(
            Token(alphas),
            Token(Literal('=')),
            Token(positive_integer),
        )
        self.p2 = Sequence(
            Token(alphas),
            Discard(Token(Literal('='))),
            Token(positive_integer),
        )

    def test_it_should_combine_parsers_to_make_a_larger_parser(self):
        self.assertEqual(self.p1.parse_string('arst = 1234 '), (('arst', '=', 1234), ''))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p1.parse_string('arst = ')

    def test_it_should_not_include_discardable_results(self):
        self.assertEqual(self.p2.parse_string('arst = 1234 '), (('arst', 1234), ''))


class TestOptional(unittest.TestCase):
    def test_it_should_make_a_parser_optional(self):
        p1 = Optional(Literal('a'))

        self.assertEqual(p1.parse_string('arst'), ('a', 'rst'))
        self.assertEqual(p1.parse_string('rst'), (Discardable(None), 'rst'))

        p2 = Apply(
            compose(tuple, flatten),
            digits & Optional(Literal('.') & digits),
        )

        self.assertEqual(p2.parse_string('1234'), (('1234',), ''))
        self.assertEqual(p2.parse_string('1234.'), (('1234',), '.'))
        self.assertEqual(p2.parse_string('1234.1234'), (('1234', '.', '1234'), ''))


class TestApply(unittest.TestCase):
    class Statement(object):
        def __init__(self, label, value):
            self.label = label
            self.value = value

    def setUp(self):
        self.p1 = Apply(
            unary(self.Statement),
            Sequence(
                Token(alphas),
                compose(Discard, Token, Literal)('='),
                positive_integer,
            ),
        )

        self.p2 = Apply(
            compose(float, join, flatten),
            digits & Optional(Literal('.') & digits),
        )

    def test_it_should_apply_a_function_to_parser_results(self):
        x, xs = self.p1.parse_string('arst = 1234')

        self.assertIsInstance(x, self.Statement)
        self.assertEqual(x.label, 'arst')
        self.assertEqual(x.value, 1234)

        x, xs = self.p2.parse_string('1234')
        self.assertEqual(x, 1234.)

        x, xs = self.p2.parse_string('1234.')
        self.assertEqual(x, 1234.)

        x, xs = self.p2.parse_string('1234.1234')
        self.assertEqual(x, 1234.1234)


class TestAlternatives(unittest.TestCase):
    def setUp(self):
        self.p = Alternatives(
            alphas,
            digits,
        )

    def test_it_should_combine_parsers_to_make_a_larger_parser(self):
        self.assertEqual(self.p.parse_string('arst1234'), ('arst', '1234'))
        self.assertEqual(self.p.parse_string('1234arst'), ('1234', 'arst'))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p.parse_string('   arst')


class TestDiscard(unittest.TestCase):
    def test_it_should_parse_using_the_given_parser_and_mark_the_result_as_discardable(self):
        self.assertEqual(Discard(Literal('arst')).parse_string('arst'), (Discardable('arst'), ''))

    def test_it_should_accept_a_string_as_an_argument(self):
        # In this case, it should parse the given string and mark it as
        # discardable
        self.assertEqual(Discard('arst').parse_string('arst'), (Discardable('arst'), ''))
