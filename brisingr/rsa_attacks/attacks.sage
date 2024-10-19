def poly_gcd(f, g):
    if g == 0:
        # Uniqueness or something
        return f.monic()
    return poly_gcd(g, f % g)

def franklin_reiter(N, e, c1, c2, f):
    """
    """
    P.<x> = PolynomialRing(Zmod(N))

    g1 = x^e - c1
    g2 = f(x)^e - c2

    return N-(poly_gcd(g1, g2) - x)


def short_pad(N, e, c1, c2, padding_bits, eps=1/30):
    """Perform short-pad attack on RSA.

    Args:
        N: public modulus
        e: public exponent
        c1: 2^(padding_bits) * m + r1
        c2: 2^(padding_bits) * m + r2
        padding_bits: length of random padding (r1, r2)
        eps: smaller implies bigger upper bound (I think)

    Notes:
        padding_bits <= N.bit_length() // e^2

    Returns:
        Original message m, without padding.
    """
    P.<x,y> = PolynomialRing(ZZ)

    g1 = x^e - c1
    g2 = (x + y)^e - c2

    # Compute the resultant
    res = g1.resultant(g2)

    P.<y> = PolynomialRing(Zmod(N))

    # Move resultant to Zn[y]
    rres = 0
    for ci, ei in zip(res.coefficients(), res.exponents()):
        rres += ci*y^ei[1]

    # Calculate difference between paddings
    diff = rres.small_roots(epsilon=eps)[0]

    # Recover original message (including padding)
    m = franklin_reiter(N, e, c1, c2, lambda x: x + diff)

    return int(m) >> padding_bits

