import unittest

from .exceptions import NotEnoughInputError, ImproperInputError
from .parsers import (
    Take, TakeIf, TakeWhile, digits, alphas, spaces, TakeUntil, Token, word,
    TakeAll, Map, positive_integer, Accept, Discardable, Discard, Sequence,
    Optional, Alternatives,
)
from .utils import compose, flatten


class TestCompose(unittest.TestCase):
    def test_it_should_compose_the_given_functions(self):
        f = compose(
            lambda x: x + 1,
            lambda x: x * 2,
            lambda x: x ** 3,
        )

        self.assertEqual(f(1), 3)
        self.assertEqual(f(2), 17)
        self.assertEqual(f(3), 55)


class TestFlatten(unittest.TestCase):
    def test_it_should_flatten_the_given_arbitrarily_nested_list(self):
        self.assertEqual(
            flatten([1, 2, [3, 4, [5, 6]]]),
            [1, 2, 3, 4, 5, 6],
        )

        heavily_nested = reduce(lambda a, i: (a, i), range(100))
        self.assertEqual(
            flatten(heavily_nested),
            list(range(100)),
        )


class TestParserBuilding(unittest.TestCase):
    def test_it_should_allow_building_of_parser_with_bitwise_operations(self):
        p1 = alphas & digits
        self.assertEqual(p1('arst1234'), (('arst', '1234'), ''))

        p2 = alphas | digits
        self.assertEqual(p2('arst1234'), ('arst', '1234'))
        self.assertEqual(p2('1234arst'), ('1234', 'arst'))

        p3 = positive_integer | (alphas & (digits | spaces))
        self.assertEqual(
            p3('1234arst1234    '),
            (1234, 'arst1234    '),
        )
        self.assertEqual(
            p3('arst1234    1234'),
            (('arst', '1234'), '    1234'),
        )
        self.assertEqual(
            p3('arst    1234'),
            (('arst', '    '), '1234'),
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


class TestDigit(unittest.TestCase):
    def test_it_should_parse_input_chars_which_are_digits(self):
        self.assertEqual(digits('1234arst'), ('1234', 'arst'))


class TestAlpha(unittest.TestCase):
    def test_it_should_parse_input_which_is_alphabetical(self):
        self.assertEqual(alphas('arst1234'), ('arst', '1234'))


class TestSpace(unittest.TestCase):
    def test_it_should_parse_input_which_is_whitespace(self):
        self.assertEqual(spaces(' \t\n\rarst'), (' \t\n\r', 'arst'))


class TestTakeUntil(unittest.TestCase):
    def test_it_should_parse_input_until_an_occurrence_of_the_given_string(self):
        p = TakeUntil('arst')

        self.assertEqual(p('before arst after'), ('before ', 'arst after'))

    def test_it_should_raise_an_error_if_the_given_string_is_not_found(self):
        p = TakeUntil('arst')

        with self.assertRaises(ImproperInputError):
            p('before after')


class TestToken(unittest.TestCase):
    def test_it_should_parse_using_the_given_parser_and_consume_whitespace(self):
        p = Token(alphas)

        self.assertEqual(p('arst arst'), ('arst', 'arst'))
        self.assertEqual(p('arst '), ('arst', ''))
        self.assertEqual(p('arst'), ('arst', ''))


class TestTakeAll(unittest.TestCase):
    def setUp(self):
        self.p = TakeAll(word)

    def test_it_should_parse_input_using_the_given_parser_until_it_fails(self):
        self.assertEqual(self.p('arst arst arst 1234'), (('arst', 'arst', 'arst'), '1234'))

    def test_it_should_raise_an_error_if_nothing_can_be_parsed(self):
        with self.assertRaises(ImproperInputError):
            self.p('1234 arst')


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
        self.p = Sequence(
            word,
            Token(Accept('=')),
            Token(positive_integer),
        )

    def test_it_should_combine_parsers_to_make_a_larger_parser(self):
        self.assertEqual(self.p('arst = 1234 '), (('arst', '=', 1234), ''))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p('arst = ')


class TestOptional(unittest.TestCase):
    def test_it_should_make_a_parser_optional(self):
        p1 = Optional(Accept('a'))

        self.assertEqual(p1('arst'), ('a', 'rst'))
        self.assertEqual(p1('rst'), (Discardable(None), 'rst'))

        p2 = digits & Optional(Accept('.') & digits)

        self.assertEqual(p2('1234'), (('1234',), ''))
        self.assertEqual(p2('1234.'), (('1234',), '.'))
        self.assertEqual(p2('1234.1234'), (('1234', '.', '1234'), ''))


class TestConstruct(unittest.TestCase):
    class Statement(object):
        def __init__(self, label, value):
            self.label = label
            self.value = value

    def setUp(self):
        self.p1 = Map(
            self.Statement,
            Sequence(
                word,
                Discard(Token(Accept('='))),
                positive_integer,
            ),
        )

        self.p2 = Map(
            lambda *args: float(''.join(args)),
            digits & Optional(Accept('.') & digits),
        )

    def test_it_should_use_parser_results_to_construct_a_new_object(self):
        x, xs = self.p1('arst = 1234')

        self.assertIsInstance(x, self.Statement)
        self.assertEqual(x.label, 'arst')
        self.assertEqual(x.value, 1234)

        x, xs = self.p2('1234')
        self.assertEqual(x, 1234.)

        x, xs = self.p2('1234.')
        self.assertEqual(x, 1234.)

        x, xs = self.p2('1234.1234')
        self.assertEqual(x, 1234.1234)


class TestAny(unittest.TestCase):
    def setUp(self):
        self.p = Alternatives(
            alphas,
            digits,
        )

    def test_it_should_combine_parsers_to_make_a_larger_parser(self):
        self.assertEqual(self.p('arst1234'), ('arst', '1234'))
        self.assertEqual(self.p('1234arst'), ('1234', 'arst'))

    def test_it_should_raise_an_exception_if_parsing_fails(self):
        with self.assertRaises(ImproperInputError):
            self.p('   arst')


class TestDiscard(unittest.TestCase):
    def setUp(self):
        self.p = Sequence(
            word,
            compose(Discard, Token, Accept)('='),
            Token(positive_integer),
        )

    def test_it_should_allow_combined_parsers_to_discard_certain_values_in_the_result_tuple(self):
        self.assertEqual(self.p('arst = 1234 '), (('arst', 1234), ''))


if __name__ == '__main__':
    unittest.main()
