from Utils.numbers import *
from decimal import *
from Crypto.Util.number import long_to_bytes
from typing import Optional

### Wiener attack ###
# e: Public exponent
# n: Public modulus
# ct: Ciphertext (as long)
def wiener_attack(e, n, ct, prec=1000) -> Optional[dict]:
    getcontext().prec = prec
    res = attack(Decimal(e), Decimal(n), ct)
    if(res):
        res["pt"] = long_to_bytes(pow(ct, res["d"], n))
        return res
    return None

def attack(e: int, n: int, ct: int) -> Optional[dict]:
    cf = convergents(cf_expansion(e, n))

    for k, d in cf:
        if k == 0:
            continue
        phi = (e*d - 1)//k
        base = (phi - n - 1)
        if base % 2 == 0 and is_perfect_square(int(pow(base // 2, 2) - n)):
            x = base // 2
            root = (pow(base // 2, 2) - n).sqrt()
            p = -x + root
            q = -x - root
            if p * q == n:
                d = pow(int(e), -1, int(phi))
                return { "p": int(p), "q": int(q), "d": int(d) }
                break
    return None
