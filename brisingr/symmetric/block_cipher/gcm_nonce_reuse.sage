from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long, long_to_bytes
import os


def is_power_of_two(x):
    return (x & (x - 1)) == 0 and x != 0


def lift_bytes(field, x: bytes):
    A = field.gens()[0]

    # Make LSB be highest exponent
    integer = int.from_bytes(x)
    field_element = 0

    for i in range(128):
        field_element += (integer & 1) * (A ^ (127 - i))
        integer >>= 1
    return field_element


def repr_int(x):
    x = x.to_integer()
    int_repr = 0
    # Lowest exponent is MSB
    for i in range(128):
        int_repr = (int_repr << 1) + (x & 1)
        x >>= 1
    return int(int_repr)


def repr_bytes(x):
    return repr_int(x).to_bytes(16, 'big')


F = GF(2^128)


x = lift_bytes(F, b"hello")

print(x)

print(repr_bytes(x))


class GCM:
    def __init__(self, block_size):
        self.block_size = block_size
        K.<X> = GF(2)[]
        self.field = GF(2^(block_size * 8), name='A', modulus=X^128 + X^7 + X^2 + X + 1)
        self.poly_ring = PolynomialRing(self.field, 'Y')

    def to_blocks(self, data):
        return [data[i*self.block_size:(i+1)*self.block_size] for i in range(math.ceil(len(data) / self.block_size))]

    def concat_ints(a, b, bits=64):
        return long_to_bytes(a, 8) + long_to_bytes(b, 8)

    def pad(self, block):
        return block + b"\x00" * ((self.block_size - len(block)) % self.block_size)

    def ghash(self, ad: bytes, ct: bytes, auth_key, mask):
        ad_blocks = [lift_bytes(self.field, block) for block in self.to_blocks(self.pad(ad))]
        ct_blocks = [lift_bytes(self.field, block) for block in self.to_blocks(ct)]

        if isinstance(auth_key, bytes):
            auth_key = lift_bytes(self.field, auth_key)

        length_block = lift_bytes(self.field, GCM.concat_ints(8 * len(ad), 8 * len(ct)))

        g = 0
        for block in ad_blocks + ct_blocks + [length_block]:
            g += block
            g *= auth_key

        return g


gcm = GCM(16)

key = os.urandom(16)
iv = os.urandom(12)
header = b"header"
data = b"give me the flag"
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

cipher.update(header)
ciphertext, tag = cipher.encrypt_and_digest(data)

cipher = AES.new(key, AES.MODE_ECB)

ctr = iv + b"\x00\x00\x00\x01"

auth_key = cipher.encrypt(b"\x00" * 16)

tag_cipher = AES.new(key, AES.MODE_CTR, initial_value=ctr, nonce=b"")

pre_tag = repr_bytes(gcm.ghash(header, ciphertext, auth_key, b""))

real_tag = tag_cipher.encrypt(pre_tag)

assert tag == real_tag
