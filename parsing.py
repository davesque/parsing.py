class ParseError(Exception):
    pass


class NotEnoughInputError(ParseError):
    pass


class ImproperInputError(ParseError):
    pass


class Parser(object):
    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)


class Take(Parser):
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
    def __init__(self, n, f):
        super(TakeIf, self).__init__(n)

        self.f = f

    def parse(self, xs):
        x, xs = super(TakeIf, self).parse(xs)

        if not self.f(x):
            raise ImproperInputError('Condition not met for parsed input')

        return (x, xs)


class TakeWhile(TakeIf):
    def __init__(self, f):
        super(TakeWhile, self).__init__(1, f)

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


digit = TakeWhile(lambda x: x.isdigit())
alpha = TakeWhile(lambda x: x.isalpha())
space = TakeWhile(lambda x: x.isspace())


class TakeUntil(Parser):
    def __init__(self, s):
        self.s = s

    def parse(self, xs):
        try:
            i = xs.index(self.s)
        except ValueError:
            raise ImproperInputError('Substring not found in input')

        return (xs[:i], xs[i:])


class Token(Parser):
    def __init__(self, p, separation_parser=space):
        self.p = p
        self.s = separation_parser

    def parse(self, xs):
        x, xs = self.p(xs)

        try:
            _, xs = self.s(xs)
        except NotEnoughInputError:
            pass

        return (x, xs)


word = Token(alpha)


class Construct(Parser):
    def __init__(self, c, using):
        self.c = c
        self.p = using

    def parse(self, xs):
        x, xs = self.p(xs)

        return (self.c(x), xs)

positive_integer = Construct(int, digit)
