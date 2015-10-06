from StringIO import StringIO
from collections import deque


class StreamError(Exception):
    pass


class Stream(object):
    def __init__(self, s):
        self._stream = StringIO(s) if isinstance(s, basestring) else s
        self._put = deque()

    def put(self, xs):
        self._put.extendleft(reversed(xs))

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
