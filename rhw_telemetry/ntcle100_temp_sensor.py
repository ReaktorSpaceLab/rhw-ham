import math

# see datasheet for the formulas used
# www.vishay.com/docs/29049/ntcle100.pdf

A = -16.0349
B = 5459.339
C = -191141
D = -3.328322E+06

A_1 = 3.354016E-03
B_1 = 2.460382E-04
C_1 = 3.405377E-06
D_1 = 1.034240E-07
# R_REF in Hello World
R_REF = 100000


def resistance_to_celsius(resistance):
    temp = 1 / (A_1 + B_1 * math.log(resistance / R_REF) +
                C_1 * math.pow(math.log(resistance / R_REF), 2) +
                D_1 * math.pow(math.log(resistance / R_REF), 3))
    return temp - 273


def celsius_to_resistance(temp):
    temp += 273
    exponent = A + (B / temp) + (C / math.pow(temp, 2)) + (D / math.pow(temp, 3))
    return R_REF * math.exp(exponent)


