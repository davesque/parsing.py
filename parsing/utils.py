from __future__ import unicode_literals

from functools import partial
import operator


def truncate(s):
    return '{0:.10}...'.format(s) if len(s) > 10 else s


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
