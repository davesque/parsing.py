from StringIO import StringIO
import unittest

from ..streams import (
    EndOfStreamError, BeginningOfStreamError, Stream, ScrollingStream,
    CursorString, EndOfStringError,
)


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


class TestScrollingStream(unittest.TestCase):
    def setUp(self):
        self.s = ScrollingStream('arst\n1234\n\n')

    def test_it_should_be_rewindable(self):
        self.assertEqual(''.join(self.s.get(4)), 'arst')
        self.assertEqual(''.join(self.s.get(2)), '\n1')
        self.s.unget(1)
        self.assertEqual(''.join(self.s.get(1)), '1')
        self.s.unget(1)
        self.s.unget(1)
        self.assertEqual(''.join(self.s.get(1)), '\n')
        self.s.unget(5)
        self.assertEqual(''.join(self.s.get(11)), 'arst\n1234\n\n')

    def test_it_should_keep_track_of_its_position(self):
        self.assertEqual(self.s.position, (1, 1))
        self.s.get(4)
        self.assertEqual(self.s.position, (1, 5))
        self.s.get(2)
        self.assertEqual(self.s.position, (2, 2))
        self.s.unget(1)
        self.assertEqual(self.s.position, (2, 1))
        self.s.unget(1)
        self.assertEqual(self.s.position, (1, 5))
        self.s.unget(4)
        self.assertEqual(self.s.position, (1, 1))
        self.s.get(11)
        self.assertEqual(self.s.position, (4, 1))

    def test_it_should_raise_an_error_if_unget_passses_beginning_of_content(self):
        with self.assertRaises(BeginningOfStreamError):
            self.s.unget(1)

        self.s.get(4)
        with self.assertRaises(BeginningOfStreamError):
            self.s.unget(5)

    def test_if_unget_raises_an_error_should_not_jumble_content(self):
        try:
            self.s.unget(1)
        except BeginningOfStreamError:
            pass

        self.s.get(4)

        try:
            self.s.unget(5)
        except BeginningOfStreamError:
            pass

        self.s.unget(4)
        self.assertEqual(''.join(self.s.get(8)), 'arst\n123')

    def test_it_should_allow_ungetting_all_gotten_content(self):
        self.s.get(4)
        self.s.unget()
        x = self.s.get(4)
        self.assertEqual(''.join(x), 'arst')

        self.s.get()
        self.s.unget()
        x = self.s.get()
        self.assertEqual(''.join(x), 'arst\n1234\n\n')

    def test_it_should_allow_peeking_at_future_content(self):
        self.assertEqual(''.join(self.s.peek(4)), 'arst')
        self.assertEqual(''.join(self.s.get(5)), 'arst\n')
        self.assertEqual(''.join(self.s.get(4)), '1234')
        self.assertEqual(''.join(self.s.peek()), '\n\n')
        self.assertEqual(''.join(self.s.get(2)), '\n\n')

    def test_it_should_include_the_would_be_result_if_beginning_of_stream_reached(self):
        try:
            self.s.unget()
        except BeginningOfStreamError as e:
            self.assertEqual(e.result, [])

        try:
            self.s.unget(1)
        except BeginningOfStreamError as e:
            self.assertEqual(e.result, [])

        self.s.get(4)

        try:
            self.s.unget(5)
        except BeginningOfStreamError as e:
            self.assertEqual(''.join(e.result), 'arst')

    def test_comparing_should_peek_at_remaining_content_to_determine_equality(self):
        self.assertEqual(self.s, list('arst\n1234\n\n'))
        self.assertEqual(self.s.get(), list('arst\n1234\n\n'))


class TestStream(unittest.TestCase):
    def setUp(self):
        self.stream = Stream(StringIO('arstarstzxcvzxcv'))

    def test_it_should_wrap_any_object_with_a_read_method_and_provide_a_put_method(self):
        x = self.stream.get(8)
        self.assertEqual(u''.join(x), u'arstarst')

        self.stream.put(x)
        x = self.stream.get(12)
        self.assertEqual(u''.join(x), u'arstarstzxcv')

    def test_it_should_raise_an_exception_when_end_of_stream_reached(self):
        x = self.stream.get(16)
        self.assertEqual(u''.join(x), u'arstarstzxcvzxcv')

        with self.assertRaises(EndOfStreamError):
            self.stream.get(1)

        self.stream.put('arst')

        with self.assertRaises(EndOfStreamError):
            self.stream.get(5)

    def test_it_should_accept_a_string_as_an_argument(self):
        s = Stream('arst')
        self.assertEqual(''.join(s.get(4)), 'arst')

    def test_it_should_return_correct_amount_of_content_from_internal_buffer_only(self):
        x = self.stream.get(16)
        self.stream.put(x)
        x = self.stream.get(4)

        self.assertEqual(''.join(x), 'arst')

    def test_it_should_require_a_non_negative_integer(self):
        with self.assertRaises(ValueError):
            self.stream.get(-1)

    def test_it_should_allow_getting_zero_items(self):
        self.assertEqual(self.stream.get(0), [])

    def test_it_should_not_discard_content_read_while_eof_encountered(self):
        try:
            self.stream.get(17)
        except EndOfStreamError:
            pass

        x = self.stream.get(8)
        self.assertEqual(''.join(x), 'arstarst')

    def test_it_should_not_mix_up_the_order_of_putted_content(self):
        self.stream.put('5678')
        self.stream.put('1234')
        x = self.stream.get(8)
        self.assertEqual(''.join(x), '12345678')

    def test_it_should_allow_getting_all_content(self):
        x = self.stream.get()
        self.assertEqual(''.join(x), 'arstarstzxcvzxcv')

    def test_it_should_allow_getting_all_content_and_any_putted_content(self):
        self.stream.put('1234')
        x = self.stream.get()
        self.assertEqual(''.join(x), '1234arstarstzxcvzxcv')
        self.stream.put('1234')
        x = self.stream.get()
        self.assertEqual(''.join(x), '1234')

    def test_it_should_raise_an_exception_if_no_content_when_fetching_all(self):
        self.stream.get()
        with self.assertRaises(EndOfStreamError):
            self.stream.get()

    def test_it_should_include_a_result_if_end_of_stream_error_thrown_when_no_content(self):
        self.stream.get()
        try:
            self.stream.get()
        except EndOfStreamError as e:
            self.assertEqual(e.result, [])

    def test_it_should_include_a_result_if_end_of_stream_error_thrown_when_not_enough_content(self):
        try:
            self.stream.get(17)
        except EndOfStreamError as e:
            self.assertEqual(''.join(e.result), 'arstarstzxcvzxcv')
