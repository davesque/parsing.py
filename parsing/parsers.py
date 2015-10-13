from .exceptions import ParseError, NotEnoughInputError, ImproperInputError
from .utils import truncate, equals


class Parser(object):
    def __call__(self, xs):
        return self.parse(xs)

    def __and__(self, other):
        return Sequence(self, other)

    def __or__(self, other):
        return Alternatives(self, other)


class TakeItems(Parser):
    """
    Constructs a parser which takes ``n`` items.
    """
    def __init__(self, n):
        # n must be positive
        if n < 1:
            raise ValueError('Must provide integer greater than zero')

        self.n = n

    def parse(self, xs):
        n = self.n

        # If sequence not long enough, raise
        if n > len(xs):
            raise NotEnoughInputError('Expected at least {0} char(s) in string "{1}"'.format(
                n,
                truncate(xs),
            ))

        return (xs[:n], xs[n:])


class TakeIf(Parser):
    """
    Constructs a parser which parses the given input with a parser ``p`` if a
    predicate ``f`` returns ``True`` for the result of ``p``.
    """
    def __init__(self, p, f):
        self.p = p
        self.f = f

    def parse(self, xs):
        x, xs = self.p(xs)

        if not self.f(x):
            raise ImproperInputError('Condition not met for "{0}" parsed from "{1}"'.format(
                truncate(x),
                truncate(xs),
            ))

        return (x, xs)

    def __invert__(self):
        return TakeIf(self.p, lambda x: not self.f(x))


class TakeItemsIf(TakeIf):
    """
    Constructs a parser which takes ``n`` items if the given predicate ``f``
    returns ``True`` for the parsed items.
    """
    def __init__(self, n, f):
        super(TakeItemsIf, self).__init__(TakeItems(n), f)


class Literal(TakeItemsIf):
    """
    Constructs a parser which parses the given string ``s``.
    """
    def __init__(self, s):
        super(Literal, self).__init__(len(s), equals(s))


class TakeWhile(TakeItemsIf):
    """
    Constructs a parser which takes items as long as the given predicate ``f``
    returns ``True`` for the parsed items.
    """
    def __init__(self, f):
        super(TakeWhile, self).__init__(1, f)

    def parse(self, xs):
        result = []

        i = 0
        while True:
            try:
                x, xs_ = super(TakeWhile, self).parse(xs)
            except ParseError as e:
                # If no parsing can be done at all, raise an error
                if i == 0:
                    raise e

                return (''.join(result), xs)

            result.append(x)
            xs = xs_

            i += 1


class TakeUntil(Parser):
    """
    Constructs a parser which takes items until the given parser ``p``
    succeeds.
    """
    move = TakeItems(1)

    def __init__(self, p):
        self.p = Literal(p) if isinstance(p, basestring) else p

    def parse(self, xs):
        xs_ = xs

        result = []
        i = 0
        while True:
            try:
                _, _ = self.p(xs)
                break
            except ParseError:
                pass

            try:
                x, xs = self.move(xs)
                result.append(x)
            except NotEnoughInputError:
                raise ImproperInputError('Terminal parser never succeeded in string "{0}"'.format(
                    truncate(xs_),
                ))

            i += 1

        if i == 0:
            raise ImproperInputError('No content captured before terminal parser succeeded in string "{0}"'.format(
                truncate(xs_),
            ))

        return (''.join(result), xs)


class TakeAll(Parser):
    """
    Augments the given parser ``p`` to continue applying itself to the input as
    long as parsing with ``p`` succeeds.  If no input can be parsed at all with
    ``p``, raises an exception.
    """
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


class Token(Parser):
    """
    Augments the given parser ``p`` to expect and consume whitespace after any
    items successfully parsed by ``p``.  The parser ``separation_parser`` can
    be provided to customize whitespace parsing behavior.
    """
    def __init__(self, p, separation_parser=None):
        self.p = p

        if separation_parser:
            self.s = separation_parser
        else:
            from .basic import spaces
            self.s = spaces

    def parse(self, xs):
        x, xs = self.p(xs)

        try:
            _, xs = self.s(xs)
        except NotEnoughInputError:
            pass

        return (x, xs)


class Discardable(object):
    def __init__(self, result):
        self.result = result

    def __eq__(self, other):
        return (
            (self.result is None and other.result is None) or
            (self.result == other.result)
        )


class Discard(Parser):
    """
    Augments the given parser ``p`` to return a discardable value when parsing
    succeeds.  Discardable values are not included in the results of compound
    ``Sequence`` parsers.
    """
    def __init__(self, p):
        self.p = Literal(p) if isinstance(p, basestring) else p

    def parse(self, xs):
        x, xs = self.p(xs)
        return (Discardable(x), xs)


class Optional(Parser):
    """
    Augments the given parser ``p`` to return a discardable ``None`` value
    instead of raising an exception when parsing fails.
    """
    def __init__(self, p):
        self.p = p

    def parse(self, xs):
        try:
            return self.p(xs)
        except ParseError:
            return (Discardable(None), xs)


class Compound(Parser):
    def __init__(self, *ps):
        self.ps = ps


class Sequence(Compound):
    """
    Constructs a compound parser with the given parsers ``ps``.  The compound
    parser will return the results of all parsers in ``ps`` as a flattened
    tuple.  It fails if any parser in ``ps`` fails.
    """
    def parse(self, xs):
        result = []

        xs_ = xs

        try:
            for p in self.ps:
                x, xs = p(xs)
                # Don't include result if discardable
                if not isinstance(x, Discardable):
                    result.append(x)

        except ParseError:
            raise ImproperInputError('Sequence not found in string "{0}"'.format(
                truncate(xs_),
            ))

        return (tuple(result), xs)


class Alternatives(Compound):
    """
    Constructs a compound parser with the given parsers ``ps``.  The compound
    parser will return the result of the first parser in ``ps`` which parses
    the input successfully.  It fails if no parsers in ``ps`` succeed.
    """
    def parse(self, xs):
        for p in self.ps:
            try:
                return p(xs)
            except ParseError:
                pass

        raise ImproperInputError('No alternatives found in string "{0}"'.format(
            truncate(xs),
        ))


class Apply(Parser):
    """
    Augments the given parser ``p`` to apply the given function ``f`` to its
    result before returning it.
    """
    def __init__(self, f, p):
        self.f = f
        self.p = p

    def parse(self, xs):
        x, xs = self.p(xs)
        return (self.f(x), xs)
