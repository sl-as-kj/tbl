#!/usr/bin/env python
"""
Module to perform fixed-width formatting
"""
import math

ELLIPSIS = '\u2026'

PAD_SPACE = object()  # pad numbers with spaces
PAD_ZERO = object()  # pad numbers with zeros
SIGN_NEGATIVE = object()
SIGN_ALWAYS = object()
SIGN_NONE = object()
SCALE_PERCENT = object()
SCALE_BASIS_POINTS = object()


class String(object):
    """
    A fixed-width formatter for string objects
    """
    def __init__(self, width=5, ellipsis='\u2026', pad=' ', position=1.0, pad_left=False):
        """

        :param width:
        :param ellipsis: the character to use for shortening
        :param pad: the character to use for padding
        :param position: the position at which elision occurs
        :param pad_left:
        """
        self.width = width
        self.ellipsis = ellipsis
        self.pad = pad
        self.position = position
        self.pad_left = pad_left

    def __call__(self, value):
        """
        Default call -- can be obviously improved in almost every situation

        :param value: the value to format
        :return: a string expression for the value
        """
        str_val = str(value)
        if len(str_val) > self.width:
            ellision_index = int((self.width - 1) * self.position)
            if ellision_index == 0:
                return self.ellipsis + str_val[-(self.width - 1):]
            if ellision_index == (self.width - 1):
                return str_val[:ellision_index] + self.ellipsis
            return str_val[:ellision_index] + self.ellipsis + str_val[-(self.width - ellision_index):]
        if self.pad_left:
            return self.pad * (self.width - len(str_val)) + str_val[:self.width]
        else:
            return str_val[:self.width] + self.pad * (self.width - len(str_val))


class Bool(String):
    """
    A fixed-width formatter for boolean objects
    """
    def __init__(self, true_str='True', false_str='False', width=None, pad_left=False):
        super().__init__(width=width or max(len(true_str), len(false_str)), pad_left=pad_left)
        self.true_str = true_str
        self.false_str = false_str

    def __call__(self, value):
        return super().__call__(self.true_str if bool(value) else self.false_str)


class Number(object):
    """
    A fixed-width format for integer and floating-point types
    """
    def __init__(self, size=8, precision=None, sign=SIGN_NEGATIVE, pad=' ', point='.', nan='NaN', inf='inf',
                 bad='#', scale=None):
        """

        :param size: number of integral digits
        :param precision: number of fractional digits (0 = decimal point but no digits)
        :param sign:
        :param pad:
        :param point:
        :param nan:
        :param inf:
        :param bad:
        """
        self.size = size
        self.precision = precision
        assert sign in (SIGN_NEGATIVE, SIGN_ALWAYS, SIGN_NONE)  # if we assert, we need to control setters too...
        self.sign = sign
        self.pad = pad
        self.point = point
        self.nan = nan
        self.inf = inf
        self.bad = bad
        self.scale = scale

    @property
    def width(self):
        return (0 if self.sign == SIGN_NONE else 1) + self.size + (0 if self.precision is None else self.precision + 1)

    def __call__(self, value):


        width = self.width
        if math.isnan(value):
            return String(width)(self.nan)

        if math.isinf(value):
            if self.sign is SIGN_NONE:
                sign = ''
            elif self.sign is SIGN_NEGATIVE:
                sign = '-' if value < 0 else ' '
            else:
                sign = '-' if value < 0 else '+'
            return sign + String(width-1)(self.inf)

        if self.sign is SIGN_NONE:
            assert value >= 0
            sign = '-'
        elif self.sign is SIGN_NEGATIVE:
            sign = ' '
        elif self.sign is SIGN_ALWAYS:
            sign = '+'
        else:
            raise ValueError('sign is not a valid value')

        if self.precision is None:
            precision, width_adj, addtl = '.0', 0, ''
        elif self.precision == 0:
            precision, width_adj, addtl = '.0', -1, '.'
        else:
            precision, width_adj, addtl = '.'+str(self.precision), 0, ''

        format_str = '{fill}{align}{sign}{width}{precision}F'.format(fill=self.pad,
                                                                     align='>',
                                                                     sign=sign,
                                                                     width=width + width_adj,
                                                                     precision=precision)
        format_str = '{:' + format_str + '}' + addtl
        print(format_str)
        rtn = format_str.format(value + 0.0)  # add zero to remove minus zero
        return self.bad * width if len(rtn) > width else rtn
