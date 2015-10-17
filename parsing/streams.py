from __future__ import unicode_literals

from StringIO import StringIO
from collections import deque


class EndOfStringError(Exception):
    def __init__(self, msg, result=None):
        super(EndOfStringError, self).__init__(msg)
        self.result = result


class StreamError(Exception):
    pass


class EndOfStreamError(StreamError):
    def __init__(self, msg, result):
        super(StreamError, self).__init__(msg)
        self.result = result


class BeginningOfStreamError(EndOfStreamError):
    pass


class CursorString(object):
    def __init__(self, s, line=1, col=1):
        self._s = s
        self._line = line
        self._col = col

    @property
    def position(self):
        return self._line, self._col

    def __eq__(self, other):
        if isinstance(other, CursorString):
            return self._s == other._s

        return self._s == other

    def __str__(self):
        return self._s

    def read(self, n=None):
        s = self._s

        if len(s) == 0:
            raise EndOfStringError('End of string reached')

        if n is None:
            x, xs = s, ''
        elif n < 0:
            raise ValueError('Cannot read negative amount of chars from string')
        else:
            x, xs = s[:n], s[n:]

        if len(x) < n:
            raise EndOfStringError('End of string reached', x)

        ls = x.split('\n')
        dl, dc = len(ls) - 1, len(ls[-1])

        return (x, type(self)(
            xs,
            self._line + dl,
            self._col + dc if dl == 0 else 1 + dc,
        ))

    def get_error(self, ErrorClass, msg):
        p = self.position

        return ErrorClass('At line {0}, col {1}: {2}'.format(
            p[0], p[1], msg,
        ))


class Stream(object):
    def __init__(self, s):
        self._stream = StringIO(s) if isinstance(s, basestring) else s
        self._put = deque()

    def put(self, xs):
        self._put.extendleft(reversed(xs))

    def get(self, n=None):
        if n is not None and n < 0:
            raise ValueError('Cannot request negative amounts of items')

        result = []

        if n is None:
            result.extend(self._put)
            self._put.clear()
            result.extend(self._stream.read())

            if len(result) == 0:
                raise EndOfStreamError('End of stream reached', result=result)

        else:
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
                raise EndOfStreamError('End of stream reached', result=result)

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

    def unget(self, n=None):
        buf = self._buf

        if n is None:
            xs = buf
            if len(xs) == 0:
                raise BeginningOfStreamError('Beginning of stream reached', result=xs)
            self._buf = []
        else:
            xs = buf[-n:]
            if len(xs) != n:
                raise BeginningOfStreamError('Beginning of stream reached', result=xs)
            buf[-n:] = []

        self.put(xs)

        for x in xs:
            if x != '\n':
                self._column -= 1
            else:
                self._column = self._line_columns.pop()
                self._line -= 1

    def peek(self, n=None):
        xs = self.get(n)
        self.unget(len(xs))
        return xs

    @property
    def position(self):
        return self._line, self._column

    def get_error(self, ErrorClass, msg):
        pos = self.position

        return ErrorClass('At line {0}, col {1}: {2}'.format(
            pos[0],
            pos[1],
            msg,
        ))

    def __eq__(self, other):
        return self.peek() == list(other)
