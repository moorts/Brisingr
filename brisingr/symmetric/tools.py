from collections import Counter
import string

from vigenere import Vigenere


def index_of_coincidence(text, ALPHABET=string.ascii_lowercase):
    """Calculate index of coincidence for given text.

    See: https://en.wikipedia.org/wiki/Index_of_coincidence.
    """
    frequencies = Counter(text).values()
    N = len(text)
    c = len(ALPHABET)

    return c * sum(freq*(freq - 1)/(N*(N-1)) for freq in frequencies)

def find_period(ct, BASE_IOC=1.73, ALPHABET=string.ascii_lowercase):
    ct = list(filter(lambda c: c in ALPHABET, ct))
    deviations = []
    for period in range(1, 10):
        ioc = 0
        for i in range(period):
            same_key = []
            for j in range(len(ct) // period):
                same_key.append(ct[j*period + i])
            ioc += index_of_coincidence(same_key, ALPHABET=ALPHABET)/period
        deviations.append(abs(ioc - BASE_IOC))

    print(deviations)
    return deviations.index(min(deviations)) + 1


KEY = "caesar"
cipher = Vigenere(KEY)

pt = "this is some random english text, which was apparently not long enough but maybe now. it seems like it's still not big enough, but no matter I'm just gonna add more text, but to be honest its a bit disheartening that it doesn't work for small texts."

ct = cipher.encrypt(pt)

print(ct)

print(find_period(ct), len(KEY))
