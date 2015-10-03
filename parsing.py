import operator


class ParseError(Exception):
    pass


class NotEnoughInputError(ParseError):
    pass


class ImproperInputError(ParseError):
    pass


def truncate(s):
    return s[:10] + '...' if len(s) > 10 else s


is_digit = operator.methodcaller('isdigit')
is_alpha = operator.methodcaller('isalpha')
is_space = operator.methodcaller('isspace')


class Parser(object):
    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)

    def __and__(self, other):
        return All(self, other)

    def __or__(self, other):
        return Any(self, other)


class Take(Parser):
    def __init__(self, n):
        if n < 1:
            raise ValueError('Must provide integer greater than zero')

        self.n = n

    def parse(self, xs):
        n = self.n

        if n > len(xs):
            raise NotEnoughInputError('Expected at least {0} char(s) in string "{1}"'.format(
                n,
                truncate(xs),
            ))

        return (xs[:n], xs[n:])


class TakeIf(Take):
    def __init__(self, n, f):
        super(TakeIf, self).__init__(n)

        self.f = f

    def parse(self, xs):
        x, xs = super(TakeIf, self).parse(xs)

        if not self.f(x):
            raise ImproperInputError('Condition not met for "{0}" parsed from "{1}"'.format(
                truncate(x),
                truncate(xs),
            ))

        return (x, xs)

    def __invert__(self):
        n, f = self.n, self.f
        return type(self)(n, lambda x: not f(x))


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


digits = TakeWhile(is_digit)
alphas = TakeWhile(is_alpha)
spaces = TakeWhile(is_space)


class TakeUntil(Parser):
    def __init__(self, s):
        self.s = s

    def parse(self, xs):
        s = self.s

        try:
            i = xs.index(s)
        except ValueError:
            raise ImproperInputError('Substring "{0}" not found in string "{1}"'.format(
                truncate(s),
                truncate(xs),
            ))

        return (xs[:i], xs[i:])


class Token(Parser):
    def __init__(self, p, separation_parser=spaces):
        self.p = p
        self.s = separation_parser

    def parse(self, xs):
        x, xs = self.p(xs)

        try:
            _, xs = self.s(xs)
        except NotEnoughInputError:
            pass

        return (x, xs)


word = Token(alphas)


class TakeAll(Parser):
    def __init__(self, p):
        self.p = p

    def parse(self, xs):
        result = []

        i = 0
        while True:
            try:
                x, xs = self.p(xs)
            except ParseError:
                if i == 0:
                    raise ImproperInputError('Could not parse anything from string "{0}"'.format(
                        truncate(xs),
                    ))

                break

            result.append(x)

            i += 1

        return (tuple(result), xs)


class Construct(Parser):
    def __init__(self, c, using):
        self.c = c
        self.p = using

    def parse(self, xs):
        x, xs = self.p(xs)

        return (self.c(x), xs)

positive_integer = Construct(int, digits)


class Accept(TakeIf):
    def __init__(self, s):
        super(Accept, self).__init__(len(s), lambda x: x == s)


class Compound(Parser):
    def __init__(self, *ps):
        self.ps = ps


class All(Compound):
    def parse(self, xs):
        result = []

        xs_ = xs

        try:
            for p in self.ps:
                x, xs = p(xs)
                result.append(x)
        except ParseError:
            raise ImproperInputError('String "{0}" could not be parser by conjunctive parser'.format(
                truncate(xs_),
            ))

        return (tuple(result), xs)


class Any(Compound):
    def parse(self, xs):
        for p in self.ps:
            try:
                return p(xs)
            except ParseError:
                pass

        raise ImproperInputError('String "{0}" could not be parsed by disjunctive parser'.format(
            truncate(xs),
        ))
