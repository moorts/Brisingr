from decimal import *
getcontext().prec = 1000

def cube_root(x): 
    d1 = Decimal(1)
    d2 = Decimal(2)
    d3 = Decimal(3)

    x0 = (x-d1)/d3
    xn = (d2 * x0 + x / Decimal(x0*x0) ) / d3

    while xn != x0:
        x0 = xn
        xn = (d2 * x0 + x / Decimal(x0*x0) ) / d3

    return xn

def convergents(e):
    n = [] # Nominators
    d = [] # Denominators

    for i in range(len(e)):
        if i == 0:
            ni = e[i]
            di = 1
        elif i == 1:
            ni = e[i]*e[i-1] + 1
            di = e[i]
        else: # i > 1
            ni = e[i]*n[i-1] + n[i-2]
            di = e[i]*d[i-1] + d[i-2]

        n.append(ni)
        d.append(di)
        yield (ni, di)

def cf_expansion(n, d):
    e = []

    q = n // d
    r = n % d
    e.append(q)

    while r != 0:
        n, d = d, r
        q = n // d
        r = n % d
        e.append(q)

    return e
