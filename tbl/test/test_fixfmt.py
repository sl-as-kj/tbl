"""
Test of fmt.py

Unless otherwise specified, tests are adapted from https://github.com/alexhsamuel/fixfmt/blob/master/test/

"""
import math
import pytest

import fixfmt


def test_using_api_docs():
    """
    test adapted from https://github.com/alexhsamuel/fixfmt/tree/master/python
    """
    fmt = fixfmt.Bool()
    assert fmt(True) == 'True '
    assert fmt(False) == 'False'

    fmt = fixfmt.String(10)
    assert fmt('testing') == 'testing   '
    assert fmt('Hello, world!') == 'Hello, wo…'

    fmt = fixfmt.Number(3, 3)
    assert fmt(math.pi) == '   3.142'


def test_using_cxx_api_docs():
    """
    test adapted from https://github.com/alexhsamuel/fixfmt/blob/master/cxx/README.md
    """

    fmt = fixfmt.Bool()
    assert fmt(True)  == 'True '
    assert fmt(False) == 'False'

    fmt = fixfmt.Bool('Yes', 'No')
    assert fmt(True)  == 'Yes'
    assert fmt(False) == 'No '

    fmt = fixfmt.String(10)
    assert fmt('testing')       == 'testing   '
    assert fmt('Hello, world!') == 'Hello, wo…'

    x = 123.45678
    assert fixfmt.Number(5, 1)(x) == '   123.5'
    assert fixfmt.Number(3, 3)(x) == ' 123.457'

    assert fixfmt.Number(5)(x) == '   123'


@pytest.mark.parametrize('index', range(-5, 6, 1))
def test_indexing(index):
    print('=', 'happy'[index:])
    # print('=', 'happy'[:index])


def test_number_int():
    fmt = fixfmt.Number(3)
    assert fmt.width == 4
    assert '   0' == fmt(    0)
    assert '   0' == fmt(   -0)
    assert '   1' == fmt(    1)
    assert '  -1' == fmt(   -1)
    assert '   9' == fmt(    9)
    assert ' -11' == fmt(  -11)
    assert '  50' == fmt(   50)
    assert ' -99' == fmt(  -99)
    assert ' 100' == fmt(  100)
    assert '-101' == fmt( -101)
    assert ' 999' == fmt(  999)
    assert '-999' == fmt( -999)
    assert '####' == fmt( 1000)
    assert '####' == fmt(-1000)
    assert '####' == fmt(98765)
    assert '####' == fmt(-9999)


def test_number_double():
    fmt = fixfmt.Number(2, 3)
    assert fmt.width == 7
    assert '  0.000' == fmt(0.0)
    assert '  0.000' == fmt(-0.0)
    assert '  1.000' == fmt(1.0)
    assert ' -1.000' == fmt(-1.0)
    assert '  0.000' == fmt(0.0004)
    assert ' -0.000' == fmt(-0.0004)
    assert ' -1.000' == fmt(-1.0)
    assert '  0.001' == fmt(0.00051)
    assert ' -0.001' == fmt(-0.00051)
    assert '  0.001' == fmt(0.0014)
    assert ' -0.001' == fmt(-0.0014)
    assert '  0.002' == fmt(0.0015)
    assert ' -0.002' == fmt(-0.0015)
    assert '  0.002' == fmt(0.00151)
    assert ' -0.002' == fmt(-0.00151)
    assert '  0.008' == fmt(0.0084)
    assert '  0.009' == fmt(0.0085)
    assert '  0.009' == fmt(0.0086)
    assert ' -0.009' == fmt(-0.0094)
    assert ' -0.009' == fmt(-0.0095)
    assert ' -0.010' == fmt(-0.0096)
    assert '  5.999' == fmt(5.9994)
    assert '  5.999' == fmt(5.99949)
    assert '  6.000' == fmt(5.9995)
    assert '  6.000' == fmt(5.99951)
    assert '-12.234' == fmt(-12.2344)
    assert '-12.234' == fmt(-12.23449)
    assert '-12.235' == fmt(-12.2345)
    assert '-12.235' == fmt(-12.23451)
    assert ' 43.499' == fmt(43.499)
    assert ' 43.500' == fmt(43.4999)
    assert ' 43.500' == fmt(43.5)
    assert ' 43.502' == fmt(43.502)
    assert ' 43.800' == fmt(43.7995)
    assert ' 99.000' == fmt(99)
    assert '-99.000' == fmt(-99)
    assert ' 99.999' == fmt(99.999)
    assert '-99.999' == fmt(-99.999)
    assert ' 99.999' == fmt(99.9994)
    assert '-99.999' == fmt(-99.9994)
    assert ' 99.999' == fmt(99.9995)
    assert '-99.999' == fmt(-99.9995)
    assert '#######' == fmt(100)
    assert '#######' == fmt(-100)
    assert '#######' == fmt(999)
    assert '#######' == fmt(-999)
    assert 'NaN    ' == fmt(math.nan)
    assert 'NaN    ' == fmt(-math.nan)
    assert ' inf   ' == fmt(math.inf)
    assert '-inf   ' == fmt(-math.inf)
    

def test_number_float_rounding():
    fmt = fixfmt.Number(1, 0)
    assert ' 0.' == fmt( 0.5)
    assert '-0.' == fmt(-0.5)
    assert ' 2.' == fmt( 1.5)
    assert '-2.' == fmt(-1.5)
    assert ' 2.' == fmt( 2.5)
    assert '-2.' == fmt(-2.5)
    assert ' 8.' == fmt( 7.5)
    assert '-8.' == fmt(-7.5)

    fmt = fixfmt.Number(1, 2)
    assert ' 0.12' == fmt( 0.125)
    assert '-0.12' == fmt(-0.125)
    assert ' 0.38' == fmt( 0.375)
    assert '-0.38' == fmt(-0.375)
    assert ' 0.62' == fmt( 0.625)
    assert '-0.62' == fmt(-0.625)
    assert ' 0.88' == fmt( 0.875)
    assert '-0.88' == fmt(-0.875)

    pass
    

# # uncomment when ready
# @pytest.mark.skip
# @pytest.mark.parametrize('i', range(-9994, 9995))
# def test_number_float_exhaustive(i):
#     fmt = fixfmt.Number(1, 2, '+')
#     val = 0.001 * i
#     expected = '{:4.2f}'.format(val)
#     actual = fmt(val)
#     assert actual == expected


def test_number_integer_size():
    assert " 4" == fixfmt.Number(1)(4)
    assert "##" == fixfmt.Number(1)(42)
    assert "##" == fixfmt.Number(1)(999)

    assert "  4" == fixfmt.Number(2)(4)
    assert " 42" == fixfmt.Number(2)(42)
    assert "###" == fixfmt.Number(2)(999)

    assert "         4" == fixfmt.Number(9)(4)
    assert "        42" == fixfmt.Number(9)(42)
    assert "       999" == fixfmt.Number(9)(999)
    assert "##########" == fixfmt.Number(9)(1e+12)


def test_number_float_precision():
    assert '-123' == fixfmt.Number(3, None)(-123.45678)
    assert '-123.' == fixfmt.Number(3, 0)(-123.45678)
    assert '-123.5' == fixfmt.Number(3, 1)(-123.45678)
    assert '-123.46' == fixfmt.Number(3, 2)(-123.45678)
    assert '-123.457' == fixfmt.Number(3, 3)(-123.45678)
    assert '-123.4568' == fixfmt.Number(3, 4)(-123.45678)
    assert '-123.45678' == fixfmt.Number(3, 5)(-123.45678)


def test_number_int_pad():
    assert '  42.' == fixfmt.Number(3, 0, pad=' ')( 42)
    assert ' -42.' == fixfmt.Number(3, 0, pad=' ')(-42)
    assert ' 042.' == fixfmt.Number(3, 0, pad='0')( 42)
    assert '-042.' == fixfmt.Number(3, 0, pad='0')(-42)
    


def test_number_int_sign():
    assert '     42.' == fixfmt.Number(6, 0, fixfmt.SIGN_NEGATIVE)( 42)
    assert '    -42.' == fixfmt.Number(6, 0, fixfmt.SIGN_NEGATIVE)(-42)
    assert ' 000042.' == fixfmt.Number(6, 0, pad='0')( 42)
    assert '-000042.' == fixfmt.Number(6, 0, pad='0')(-42)

    assert '    +42.' == fixfmt.Number(6, 0, fixfmt.SIGN_ALWAYS)( 42)
    assert '    -42.' == fixfmt.Number(6, 0, fixfmt.SIGN_ALWAYS)(-42)
    assert '+000042.' == fixfmt.Number(6, 0, sign='+', pad='0')( 42)
    assert '-000042.' == fixfmt.Number(6, 0, sign='+', pad='0')(-42)

    assert '    42.' == fixfmt.Number(6, 0, pad=' ', sign=fixfmt.SIGN_NONE)( 42)
    assert '#######' == fixfmt.Number(6, 0, pad=' ', sign=fixfmt.SIGN_NONE)(-42)
    assert '000042.' == fixfmt.Number(6, 0, pad='0', sign=fixfmt.SIGN_NONE)( 42)
    assert '#######' == fixfmt.Number(6, 0, pad='0', sign=fixfmt.SIGN_NONE)(-42)


def test_number_nan():
    assert 'N' == fixfmt.Number(1, -1, fixfmt.SIGN_NONE)(math.nan)
    assert 'Na' == fixfmt.Number(2, -1, fixfmt.SIGN_NONE)(math.nan)
    assert 'NaN' == fixfmt.Number(3, -1, fixfmt.SIGN_NONE)(math.nan)
    assert 'NaN   ' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, nan="NaN")(math.nan)
    assert 'nan   ' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, nan="nan")(math.nan)
    assert 'NotANu' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, nan="NotANumber")(math.nan)
    assert '  NotANumber' == fixfmt.Number(12, -1, fixfmt.SIGN_NONE, nan="NotANumber")(math.nan)


def test_number_infinity():
    assert 'i' == fixfmt.Number(1, -1, fixfmt.SIGN_NONE)(math.inf)
    assert 'in' == fixfmt.Number(2, -1, fixfmt.SIGN_NONE)(math.inf)
    assert 'inf' == fixfmt.Number(3, -1, fixfmt.SIGN_NONE)(math.inf)
    assert '###' == fixfmt.Number(3, -1, fixfmt.SIGN_NONE)(-math.inf)
    assert ' inf' == fixfmt.Number(3, -1, fixfmt.SIGN_NEGATIVE)(math.inf)
    assert '-inf' == fixfmt.Number(3, -1, fixfmt.SIGN_NEGATIVE)(-math.inf)
    assert '+inf' == fixfmt.Number(3, -1, fixfmt.SIGN_ALWAYS)(math.inf)
    assert '-inf' == fixfmt.Number(3, -1, fixfmt.SIGN_ALWAYS)(-math.inf)
    
    assert ' inf  ' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, inf="inf")(math.inf)
    assert ' INF  ' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, inf="INF")(math.inf)
    assert ' infin' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, inf="infinity")(math.inf)
    assert '+infin' == fixfmt.Number(2, 2, fixfmt.SIGN_ALWAYS, inf="infinity")(math.inf)
    assert '-infin' == fixfmt.Number(2, 2, fixfmt.SIGN_NEGATIVE, inf="infinity")(-math.inf)
    
    assert '    infinity' == fixfmt.Number(12, -1, fixfmt.SIGN_NONE, inf="infinity")(math.inf)
    assert '   -infinity' == fixfmt.Number(11, -1, fixfmt.SIGN_NEGATIVE, inf="infinity")(-math.inf)
    assert '############' == fixfmt.Number(12, -1, fixfmt.SIGN_NONE, inf="infinity")(-math.inf)

def test_number_infinity_format():
    fmt = fixfmt.Number(1, None, fixfmt.SIGN_NEGATIVE, nan="NaN", inf='\u221e')
    assert ' 5' == fmt(5)
    assert ' \u221e' == fmt( math.inf)
    assert '-\u221e' == fmt(-math.inf)


def test_number_scale():
    fmt = fixfmt.Number(3, 1, scale={1e6, 'M'})
    assert 7 == fmt.width
    assert ' 100.0M' == fmt(         1E+8  )
    assert '  12.3M' == fmt(  12345678     )
    assert '  12.3M' == fmt(  12345678.0   )
    assert ' 123.5M' == fmt( 123456789     )
    assert '-234.6M' == fmt(-234567890     )
    assert '   1.0M' == fmt(         1.0E+6)
    assert '  -0.1M' == fmt(   -100000     )
    assert '   0.1M' == fmt(     50001     )


def test_number_scale_percent():
    fmt = fixfmt.Number(3, 1, fixfmt.SIGN_NONE, scale=fixfmt.SCALE_PERCENT)
    assert '  0.0%' == fmt(0)
    assert '  0.0%' == fmt(0.0)
    assert ' 50.0%' == fmt(0.5)
    assert '100.0%' == fmt(1)
    assert '100.0%' == fmt(1.0)


def test_number_scale_bps():
    fmt =fixfmt.Number(5, scale=fixfmt.SCALE_BASIS_POINTS)
    assert '     0 bps' == fmt( 0.00001)
    assert '     1 bps' == fmt( 0.0001 )
    assert '   100 bps' == fmt( 0.01   )
    assert '  -100 bps' == fmt(-0.01   )
    assert ' 10000 bps' == fmt( 1      )
    assert '-50000 bps' == fmt(-5      )


def test_number_scale_special():
    fmt = fixfmt.Number(3, 1, scale={1e-6, 'M'})
    assert ' NaN   ' == fmt(math.nan)
    assert ' inf   ' == fmt(math.inf)
    assert '-inf   ' == fmt(-math.inf)
