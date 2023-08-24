from ..Utils.numbers import *
from decimal import *
from Crypto.Util.number import bytes_to_long, long_to_bytes
from typing import Optional, NamedTuple
import math

class AttackResult(NamedTuple):
    p: int
    q: int
    d: int
    plaintext: bytes

def wiener_attack(e: int, n: int, ct: int|bytes, prec: int=1000) -> Optional[AttackResult]:
    """Perform Wiener's Attack to break RSA

    Recovers key in linear time for small private exponents d < (1/3)n^(1/4).

    Args:
        e: public exponent
        n: public modulus
        ct: ciphertext
        prec: digits of precision for decimal arithmetic

    Returns:
        If attack succeeds returns factorization of n, private exponent d and plaintext.
        Otherwise returns None.
    """
    getcontext().prec = prec

    if type(ct) == bytes:
        ct = bytes_to_long(ct)

    res = attack(Decimal(e), Decimal(n))
    if(res):
        p, q, d = res
        plaintext = long_to_bytes(pow(ct, d, n))
        return AttackResult(p, q, d, plaintext)
    return None

def attack(e: int, n: int, prec: int=1000) -> Optional[tuple[int, int, int]]:
    getcontext().prec = prec
    cf = convergents(cf_expansion(e, n))

    for k, d in cf:
        if k == 0:
            continue
        phi = (e*d - 1)//k
        base = (phi - n - 1)
        if base % 2 == 0 and is_perfect_square(int(pow(base // 2, 2) - n)):
            x = base // 2
            root = math.isqrt(int(pow(base // 2, 2) - n))
            p = -x + root
            q = -x - root
            if p * q == n:
                d = pow(int(e), -1, int(phi))
                return (int(p), int(q), int(d))
    return None
