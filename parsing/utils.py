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
        self.stream = StringIO(s) if isinstance(s, basestring) else s

        self._put = deque()

    def put(self, x):
        self._put.extend(x)

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

        result.extend(self.stream.read(i))

        if len(result) != n:
            self.put(result)
            raise StreamError('End of stream reached')

        return result
