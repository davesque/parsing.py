from StringIO import StringIO
from collections import deque
from functools import partial
import operator


def truncate(s):
    return s[:10] + '...' if len(s) > 10 else s


def join(xs):
    return ''.join(xs)


def unary(f):
    return lambda args: f(*args)


def equals(x):
    return partial(operator.eq, x)


def compose(*fs):
    def composed(x):
        return reduce(lambda x, f: f(x), reversed(fs), x)

    return composed


def flatten(seq, seqtypes=(list, tuple)):
    # Make copy and cast to list
    seq = list(seq)

    # Flatten list in-place
    for i, _ in enumerate(seq):
        while isinstance(seq[i], seqtypes):
            seq[i:i + 1] = seq[i]

    return seq


is_digit = operator.methodcaller('isdigit')
is_alpha = operator.methodcaller('isalpha')
is_space = operator.methodcaller('isspace')


class StreamError(Exception):
    pass


class Stream(object):
    def __init__(self, s):
        self._stream = StringIO(s) if isinstance(s, basestring) else s
        self._put = deque()

    def put(self, xs):
        self._put.extend(xs)

    def get(self, n):
        if n < 0:
            raise StreamError('Cannot request negative amounts of items')

        result = []

        i = n
        while True:
            try:
                result.append(self._put.popleft())
                i -= 1
            except IndexError:
                break

            if i == 0:
                break

        result.extend(self._stream.read(i))

        if len(result) != n:
            self.put(result)
            raise StreamError('End of stream reached')

        return result


class ScrollingStream(Stream):
    def __init__(self, content):
        super(ScrollingStream, self).__init__(content)

        self._column = 1
        self._line = 1
        self._line_columns = []
        self._buf = []

    def get(self, *args, **kwargs):
        xs = super(ScrollingStream, self).get(*args, **kwargs)

        for x in xs:
            if x != '\n':
                self._column += 1
            else:
                self._line_columns.append(self._column)
                self._column = 1
                self._line += 1

        self._buf.extend(xs)

        return xs

    def unget(self, n):
        buf = self._buf

        if n > len(buf):
            raise StreamError('Cannot unget past beginning of original content')

        xs = buf[-n:]
        self.put(xs)
        buf[-n:] = []

        for x in xs:
            if x != '\n':
                self._column -= 1
            else:
                self._column = self._line_columns.pop()
                self._line -= 1

    @property
    def position(self):
        return self._line, self._column
