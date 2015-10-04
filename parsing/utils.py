import operator


def truncate(s):
    return s[:10] + '...' if len(s) > 10 else s


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
