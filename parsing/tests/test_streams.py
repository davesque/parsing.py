from __future__ import unicode_literals

import unittest

from ..streams import CursorString, EndOfStringError


class TestCursorString(unittest.TestCase):
    def setUp(self):
        self.s = CursorString('arst\n1234\n\n')

    def test_it_should_allow_reading_of_chars_from_front_of_string(self):
        x, _ = self.s.read(3)
        self.assertEqual(x, 'ars')

    def test_reading_should_not_mutate_cursor_string(self):
        x, _ = self.s.read(3)
        self.assertEqual(x, 'ars')

        x, _ = self.s.read(5)
        self.assertEqual(x, 'arst\n')

    def test_reading_should_split_string_after_chars_read(self):
        x, xs = self.s.read(3)
        self.assertEqual(x, 'ars')
        self.assertEqual(xs, 't\n1234\n\n')

    def test_reading_should_return_chars_read_as_plain_string(self):
        x, _ = self.s.read(3)
        self.assertIsInstance(x, basestring)

    def test_reading_should_return_chars_unread_as_cursor_string(self):
        _, xs = self.s.read(3)
        self.assertIsInstance(xs, CursorString)

    def test_reading_chars_should_change_position_in_unread_chars(self):
        self.assertEqual(self.s.position, (1, 1))

        a = self.s.read(3)[1]
        self.assertEqual(a, 't\n1234\n\n')
        self.assertEqual(a.position, (1, 4))

        b = a.read(2)[1]
        self.assertEqual(b, '1234\n\n')
        self.assertEqual(b.position, (2, 1))

        c = self.s.read(5)[1]
        self.assertEqual(b, c)
        self.assertEqual(b.position, c.position)

    def test_it_should_allow_comparison_with_other_strings_or_cursor_strings(self):
        self.assertEqual(self.s, 'arst\n1234\n\n')
        self.assertEqual(self.s, CursorString('arst\n1234\n\n'))

    def test_reading_None_chars_should_read_entire_string(self):
        x, xs = self.s.read()
        self.assertEqual(x, 'arst\n1234\n\n')
        self.assertEqual(xs, '')
        self.assertEqual(xs.position, (4, 1))

    def test_reading_anything_from_empty_string_should_raise_error(self):
        s = CursorString('')

        with self.assertRaises(EndOfStringError):
            s.read()

        with self.assertRaises(EndOfStringError):
            s.read(1)

    def test_reading_less_chars_than_requested_raises_an_error(self):
        s = CursorString('arst')

        with self.assertRaises(EndOfStringError):
            s.read(5)

        try:
            s.read(5)
        except EndOfStringError as e:
            self.assertEqual(e.result, 'arst')

    def test_reading_less_than_zero_chars_raises_an_error(self):
        with self.assertRaises(ValueError):
            self.s.read(-1)

    def test_it_can_be_cast_as_a_string(self):
        self.assertEqual(str(self.s), 'arst\n1234\n\n')

    def test_its_length_can_be_determined(self):
        self.assertEqual(len(self.s), 11)
