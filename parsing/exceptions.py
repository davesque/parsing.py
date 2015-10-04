class ParseError(Exception):
    pass


class NotEnoughInputError(ParseError):
    pass


class ImproperInputError(ParseError):
    pass
