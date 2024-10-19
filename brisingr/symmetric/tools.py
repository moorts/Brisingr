from collections import Counter
import string

from vigenere import Vigenere


def index_of_coincidence(text, ALPHABET=string.ascii_lowercase):
    """Calculate index of coincidence for given text.

    See: https://en.wikipedia.org/wiki/Index_of_coincidence.
    """
    text = list(filter(lambda c: c in ALPHABET, text))
    frequencies = Counter(text).values()
    N = len(text)
    c = len(ALPHABET)

    return c * sum(freq*(freq - 1)/(N*(N-1)) for freq in frequencies)

def find_period(ct, THRESHOLD=1.7):
    for period in range(1, len(ct) + 1):
        ioc = 0
        for i in range(period):
            same_key = []
            for j in range(len(ct) // period):
                same_key.append(ct[j*period + i])
            ioc += index_of_coincidence(same_key)/period
        print(period, ioc)
        if ioc > THRESHOLD:
            return period


KEY = "caesar"
cipher = Vigenere(KEY)

pt = "this is some random english text, which was apparently not long enough but maybe now. it seems like it's still not big enough, but no matter I'm just gonna add more text, but to be honest its a bit disheartening that it doesn't work for small texts."

ct = cipher.encrypt(pt)

print(find_period(ct))

print(index_of_coincidence(pt))
