from padding_oracle_attack import PaddingOracleAttack
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import os

class MockServer:
    def __init__(self):
        self.key = os.urandom(16)
        self.plaintext = b"flag{this_is_a_very_very_legit_flag}"

    def get_ct(self):
        iv = os.urandom(16)

        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)

        ct = cipher.encrypt(pad(self.plaintext, 16))

        return (iv+ct).hex()

    def check_padding(self, ct):
        ct = bytes.fromhex(ct)
        iv, ct = ct[:16], ct[16:]

        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(ct)

        try:
            unpad(plaintext, 16)
        except ValueError:
            good = False
        else:
            good = True

        return good

def randomized_test():
    import random

    server = MockServer()
    ct = bytes.fromhex(server.get_ct())

    def oracle(ct) -> tuple[bool, int]:
        return server.check_padding(ct.hex()), 1

    pt_alphabet = b"abcdefghijklmnopqrstuvwxyz{}_"
    pt_len = random.randint(0, 50)

    pt = bytes(random.choices(pt_alphabet, k=pt_len))

    attack = PaddingOracleAttack(oracle, 16, verbose=False)

    ct = attack.encrypt(pt)

    if not (dec := attack.decrypt(ct)) == pt:
        print(dec, pt, len(pt), len(pt) % 16)

for _ in range(100):
    randomized_test()
