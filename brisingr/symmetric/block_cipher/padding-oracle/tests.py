from padding_oracle_attack import padding_oracle_attack, PaddingOracleAttack
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import os

class MockServer:
    def __init__(self):
        self.key = os.urandom(16)
        self.plaintext = b"flag{this_is_a_very_very_legit_flag}"
        # self.plaintext = b"flag{this_is_a_very_legit_flag}"

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

server = MockServer()
ct = bytes.fromhex(server.get_ct())

def oracle(ct) -> tuple[bool, int]:
    return server.check_padding(ct.hex()), 1


# print(padding_oracle_attack(oracle, ct, 16))
plaintext = b"flag{this_is_a_very_very_legit_flag}"
pt_alphabet = b"abcdefghijklmnopqrstuvwxyz{}_" + bytes(range(16))
print(PaddingOracleAttack(oracle, ct, 16, pt_alphabet=plaintext).decrypt())

