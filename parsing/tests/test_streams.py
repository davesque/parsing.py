from StringIO import StringIO
import unittest

from ..streams import StreamError, Stream, ScrollingStream


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
        with self.assertRaises(StreamError):
            self.s.unget(1)

        self.s.get(4)
        with self.assertRaises(StreamError):
            self.s.unget(5)

    def test_if_unget_raises_an_error_should_not_jumble_content(self):
        try:
            self.s.unget(1)
        except StreamError:
            pass

        self.s.get(4)

        try:
            self.s.unget(5)
        except StreamError:
            pass

        self.s.unget(4)
        self.assertEqual(''.join(self.s.get(8)), 'arst\n123')


class TestStream(unittest.TestCase):
    def setUp(self):
        self.stream = Stream(StringIO('arst' * 2 + 'zxcv' * 2))

    def test_it_should_wrap_any_object_with_a_read_method_and_provide_a_put_method(self):
        x = self.stream.get(8)
        self.assertEqual(u''.join(x), u'arstarst')

        self.stream.put(x)
        x = self.stream.get(12)
        self.assertEqual(u''.join(x), u'arstarstzxcv')

    def test_it_should_raise_an_exception_when_end_of_stream_reached(self):
        x = self.stream.get(16)
        self.assertEqual(u''.join(x), u'arstarstzxcvzxcv')

        with self.assertRaises(StreamError):
            self.stream.get(1)

        self.stream.put('arst')

        with self.assertRaises(StreamError):
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
        with self.assertRaises(StreamError):
            self.stream.get(-1)

        self.assertEqual(self.stream.get(0), [])

    def test_it_should_not_discard_content_read_while_eof_encountered(self):
        try:
            self.stream.get(17)
        except StreamError:
            pass

        x = self.stream.get(8)
        self.assertEqual(''.join(x), 'arstarst')

    def test_it_should_not_mix_up_the_order_of_putted_content(self):
        self.stream.put('5678')
        self.stream.put('1234')

        x = self.stream.get(8)
        self.assertEqual(''.join(x), '12345678')