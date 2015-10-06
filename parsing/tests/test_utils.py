import unittest

from ..utils import compose, flatten, truncate, join, unary, equals


class TestEquals(unittest.TestCase):
    def test_it_should_return_a_function_that_compares_against_x(self):
        self.assertTrue(equals(234)(234))
        self.assertFalse(equals(234)(123))


class TestUnary(unittest.TestCase):
    def test_it_convert_a_function_into_a_unary_version_of_itself(self):
        self.assertEqual(unary(lambda x, y: x + y)([1, 2]), 3)


class TestJoin(unittest.TestCase):
    def test_it_should_join_a_sequence_into_a_string(self):
        self.assertEqual(join(list('arst')), 'arst')
        self.assertEqual(join(map(str, [1, 2, 3, 4])), '1234')


class TestTruncate(unittest.TestCase):
    def test_it_should_truncate_a_string(self):
        self.assertEqual(truncate('arst'), 'arst')
        self.assertEqual(truncate('arstarstar'), 'arstarstar')
        self.assertEqual(truncate('arstarstars'), 'arstarstar...')
        self.assertEqual(truncate('arstarstarstarstarstarstarstarst'), 'arstarstar...')


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
    def test_it_should_flatten_an_arbitrarily_nested_list(self):
        self.assertEqual(
            flatten([1, 2, [3, 4, [5, 6]]]),
            [1, 2, 3, 4, 5, 6],
        )

        heavily_nested = reduce(lambda a, i: (a, i), range(1000))
        self.assertEqual(
            flatten(heavily_nested),
            list(range(1000)),
        )
