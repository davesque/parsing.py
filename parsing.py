class Take(object):
    class TakeError(Exception):
        pass

    def __init__(self, n):
        if n < 1:
            raise self.TakeError('Must provide integer greater than zero')

        self.n = n

    def parse(self, xs):
        n = self.n

        if n > len(xs):
            raise self.TakeError('Not enough input to parse')

        return (xs[:n], xs[n:])
