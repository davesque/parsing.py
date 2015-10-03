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
        super(TakeIf, self).__init__(n)

        self.p = p

    def parse(self, xs):
        x, xs = super(TakeIf, self).parse(xs)

        if not self.p(x):
            raise ParseError('Condition not met for parsed input')

        return (x, xs)


class TakeWhile(Take):
    def __init__(self, p):
        super(TakeWhile, self).__init__(1)

        self.p = p

    def parse(self, xs):
        result = []

        while True:
            x, xs_ = super(TakeWhile, self).parse(xs)

            if not self.p(x):
                return (''.join(result), xs)

            result.append(x)
            xs = xs_
