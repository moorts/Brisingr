from sage.all import *
from Crypto.Util.number import getPrime

class LCG:
    def __init__(self, a, c, m, seed=1):
        self.a = a
        self.c = c
        self.m = m

        self.state = seed

    def seed(self, seed):
        self.state = seed

    def __next__(self):
        self.state = (self.a * self.state + self.c) % self.m

        return self.state

class TruncatedLCG:
    def __init__(self, a, c, m, bits, shift_right=True, seed=1):
        self.lcg = LCG(a, c, m, seed=seed)

        self.bits = bits
        self.shift_right = shift_right
        self.history = [seed]

    def seed(self, seed):
        self.lcg.seed(seed)
        self.history = [seed]

    def __next__(self):
        x = self.lcg.__next__()
        self.history.append(x)

        if self.shift_right:
            return x >> self.bits
        else:
            return x % 2**self.bits


def recover_lcg_m(outputs: list[int], max_samples=100):
    T = [X2 - X1 for (X2, X1) in zip(outputs[1:], outputs)]

    U = [T[i+1]*T[i-1] - T[i]**2 for i in range(1, max_samples+1)]

    return gcd(U)


def crack_lcg(outputs, a=None, c=None, m=None):
    if not m:
        m = recover_lcg_m(outputs)

    T = [X2 - X1 for (X2, X1) in zip(outputs[1:], outputs)]

    assert len(T) > 1

    for i in range(len(T)-1):
        t0, t1 = T[i], T[i+1]
        if gcd(t0, m) == 1:
            break
    else:
        return None

    a = (t1 * pow(t0, -1, m)) % m
    c = (outputs[1] - a*outputs[0]) % m

    return (a, c, m)

def crack_truncated_lcg(truncated_outputs, a, c, m, bits):
    if c != 0:
        T = [X2 - X1 for (X2, X1) in zip(outputs[1:], outputs)]
    else:
        T = truncated_outputs

    n = len(T)

    first_col = [m] + [a**k % m for k in range(1, n)]
    A = -1 * identity_matrix(n - 1)
    A = A.insert_row(0, zero_vector(n - 1))
    cols = A.columns()
    cols[0:0] = [first_col]
    A = matrix(cols).T

    B = A.LLL()

    Y = vector([t << bits for t in T])

    v = B * Y
    # Compute mk - By
    w = vector([round(RR(vi) / m) * m - vi for vi in v])

    z = B.solve_right(w)

    return z

m = getPrime(24)
a = 342
c = 0
bits = 12
lcg = TruncatedLCG(a, c, m, bits)

outputs = [next(lcg) for _ in range(5)]
print([x % 2**bits for x in lcg.history])

print(crack_truncated_lcg(outputs, a, c, m, bits))
