from Utils.numbers import *
from decimal import *
from Crypto.Util.number import long_to_bytes


### Wiener attack ###
# e: Public exponent
# n: Public modulus
# ct: Ciphertext (as long)
def wiener_attack(e, n, ct, prec=1000):
    getcontext().prec = prec
    attack(Decimal(e), Decimal(n), ct)

def attack(e, n, ct):
    cf = convergents(cf_expansion(e, n))

    for k, d in cf:
        if k == 0:
            continue
        phi = (e*d - 1)//k
        x = (phi - n -1)/2
        p = -x + (pow(x, 2) - n).sqrt()
        q = -x - (pow(x, 2) - n).sqrt()
        if p * q == n:
            print(f"Found factorization:\n{p}\n=============\n{q}")
            d = pow(int(e), -1, int(phi))
            print("Decryption:")
            print(long_to_bytes(pow(ct, int(d), int(n))))
            break
