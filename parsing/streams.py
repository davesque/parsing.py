from __future__ import unicode_literals


class EndOfStringError(Exception):
    def __init__(self, msg, result=None):
        super(EndOfStringError, self).__init__(msg)
        self.result = result


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

    def __len__(self):
        return len(self._s)

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
