class ParseError(Exception):
    pass


class NotEnoughInputError(ParseError):
    pass


class ImproperInputError(ParseError):
    pass


class Take(object):
    def __init__(self, n):
        if n < 1:
            raise ValueError('Must provide integer greater than zero')

        self.n = n

    def parse(self, xs):
        n = self.n

        if n > len(xs):
            raise NotEnoughInputError('Not enough input to parse')

        return (xs[:n], xs[n:])


class TakeIf(Take):
    def __init__(self, n, p):
        super(TakeIf, self).__init__(n)

        self.p = p

    def parse(self, xs):
        x, xs = super(TakeIf, self).parse(xs)

        if not self.p(x):
            raise ImproperInputError('Condition not met for parsed input')

        return (x, xs)


class TakeWhile(TakeIf):
    def __init__(self, p):
        super(TakeWhile, self).__init__(1, p)

    def parse(self, xs):
        result = []

        i = 0
        while True:
            try:
                x, xs_ = super(TakeWhile, self).parse(xs)
            except (NotEnoughInputError, ImproperInputError) as e:
                # If no parsing can be done at all, raise an error
                if i == 0:
                    raise e

                return (''.join(result), xs)

            result.append(x)
            xs = xs_

            i += 1


class TakeUntil(object):
    def __init__(self, s):
        self.s = s

    def parse(self, xs):
        try:
            i = xs.index(self.s)
        except ValueError:
            raise ImproperInputError('Substring not found in input')

        return (xs[:i], xs[i:])
