class ParseError(Exception):
    pass


class Take(object):
    def __init__(self, n):
        if n < 1:
            raise ValueError('Must provide integer greater than zero')

        self.n = n

    def parse(self, xs):
        n = self.n

        if n > len(xs):
            raise ParseError('Not enough input to parse')

        return (xs[:n], xs[n:])


class TakeIf(Take):
    def __init__(self, n, p):
        self.n = n
        self.p = p

    def parse(self, xs):
        x, xs = super(TakeIf, self).parse(xs)

        if not self.p(x):
            raise ParseError('Predicate failed')

        return (x, xs)
