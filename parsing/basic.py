from .parsers import TakeWhile, Apply
from .utils import is_digit, is_alpha, is_space


digits = TakeWhile(is_digit)
alphas = TakeWhile(is_alpha)
spaces = TakeWhile(is_space)
positive_integer = Apply(int, digits)
