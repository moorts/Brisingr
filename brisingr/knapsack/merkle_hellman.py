import secrets
from math import gcd
from Crypto.Util.number import long_to_bytes, bytes_to_long

class MerkleHellmanKey:
    def __init__(self, n: int):
        W = []
        current_sum = 0

        for _ in range(n):
            offset = secrets.randbits(32) + 1
            wi = current_sum + offset
            W.append(wi)
            current_sum += wi

        self.q = current_sum + secrets.randbits(32)

        self.r = secrets.randbits(32)

        while gcd(self.r, self.q) != 1:
            self.r = secrets.randbits(32)

        self.B = [self.r*wi % self.q for wi in W]
        self.W = W

    def pubkey(self):
        return self.B

    def privkey(self):
        return (self.W, self.q, self.r)

class MerkleHellman:
    def __init__(self, key: MerkleHellmanKey):
        self.B = key.pubkey()
        self.W, self.q, self.r = key.privkey()
        self.n = len(self.B)

    def encrypt(self, msg: bytes) -> bytes:
        msg_bits = map(int, bin(bytes_to_long(msg))[2:].zfill(self.n))

        c = sum(mi * bi for mi, bi in zip(msg_bits, self.B))

        return long_to_bytes(c)

    def decrypt(self, ct: bytes) -> bytes:
        c = bytes_to_long(ct)

        r_inv = pow(self.r, -1, self.q)

        c_prime = c * r_inv % self.q

        m = 0
        
        ci = c_prime

        for i, bi in enumerate(self.W[::-1]):
            if ci >= bi:
                ci -= bi
                m += pow(2, i)

        return long_to_bytes(m)



def randomized_test():
    import os

    for _ in range(1000):
        # Leading zeros suck.
        pt = os.urandom(8).strip(b"\x00")

        key = MerkleHellmanKey(64)
        cipher = MerkleHellman(key)

        ct = cipher.encrypt(pt)

        assert pt == cipher.decrypt(ct)

randomized_test()

