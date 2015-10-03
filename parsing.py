class ParsingError(Exception):
    pass


class Take(object):
    #class TakeError(Exception):
        #pass

    def __init__(self, n):
        self.n = n

    def parse(self, xs):
        n = self.n

        if n > len(xs):
            raise ParsingError('Not enough input')

        return (xs[:n], xs[n:])
