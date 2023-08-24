class Utils:

    def mult_char(c, k):
        if ord(c) < ord('A') or ord(c) > ord('Z'):
            return c
        return chr(((ord(c) - ord('A')) * k) % 26 + ord('A'))

class Caesar:
    def shift_char(c, k):
        if ord(c) < ord('A') or ord(c) > ord('Z'):
            return c
        return chr((ord(c) - ord('A') + k) % 26 + ord('A'))

    def encrypt(p, k):
        return "".join(map(lambda c: Utils.shift_char(c, k), p.upper()))
    def decrypt(c, k):
        return Caesar.encrypt(c, 26-k)

class Multiplicative:
    def encrypt(p, k):
        # k has to have multiplicative inverse
        assert gcd(k, 26) == 1
        return "".join(map(lambda c: Utils.mult_char(c, k), p.upper()))
    def decrypt(c, k):
        # k has to have multiplicative inverse
        assert gcd(k, 26) == 1
        return Multiplicative.encrypt(c, pow(k, -1, 26))

class Affine:
    def encrypt(p, k):
        s, t = k
        # s has to have multiplicative inverse
        assert gcd(s, 26) == 1
        return "".join(map(lambda c: Utils.shift_char(Utils.mult_char(c, s), t), p))
    def decrypt(c, k):
        s, t = k
        # s has to have multiplicative inverse
        assert gcd(s, 26) == 1
        return "".join(map(lambda x: Utils.mult_char(Utils.shift_char(x, -t), pow(s, -1, 26)), c))

class Vigenere:
    def gen_key(p, k):
        # Generates key sequence
        # Yields -1 for non-alphabetic characters
        key = k.upper()
        i, non_alphabetic = 0, 0
        while i < len(p):
            if not ord('A') <= ord(p[i]) <= ord('Z'):
                yield -1
                non_alphabetic += 1
            else:
                yield ord(key[(i-non_alphabetic)%len(key)]) - ord('A')
            i += 1

    def encrypt(p, k):
        return "".join(map(lambda x: Caesar.encrypt(x[0], x[1]), zip(p, Vigenere.gen_key(p, k))))
    def decrypt(c, k):
        return "".join(map(lambda x: Caesar.decrypt(x[0], x[1]), zip(c, Vigenere.gen_key(c, k))))

def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a%b)

## Sanity checks
KEY = "VOGEL"
plaintext = "HELLO THERE"
ciphertext = "CSRPZ OVKVP"
assert Vigenere.decrypt(Vigenere.encrypt(plaintext, KEY), KEY) == plaintext
assert Vigenere.encrypt(plaintext, KEY) == ciphertext
assert "".join(map(lambda x: chr(x + ord('A')), Vigenere.gen_key("HELLOL", KEY))) == "VOGELV"

"""
print(Caesar.encrypt("KARLSRUHE", 13))
print(Caesar.decrypt("UPWGGPS", ord("G")-ord("R")))


print(Multiplicative.encrypt("KARLSRUHE", 7))
print(Multiplicative.decrypt(Multiplicative.encrypt("KARLSRUHE", 7), 7))
#print(dec_mult("FYRRSF", 
for i in range(26):
    if gcd(i, 26) == 1 and Multiplicative.encrypt("Y", i) == "O":
        print(Multiplicative.encrypt("FYRRSF", i))
        break

print(Affine.decrypt("ZPCZPALLCP", (5, 8)))
print(Affine.encrypt("KARLSRUHE", (11, 17)))
"""
