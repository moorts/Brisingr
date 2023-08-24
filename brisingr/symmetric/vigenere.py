from collections import defaultdict
from typing import Generator, Optional
from sympy.ntheory import factorint

class Vigenere:
    def shift_char(c: str, shift: int) -> str:
        """Shift character to the right.

        Wraps around, preserves case, ignores non-alphabetic characters.

        Args:
            c: character to shift
            shift: shift width

        Returns:
            Character shifted by shift places
        """
        if not c.isalpha():
            return c

        base_offset = ord('a') if c.islower() else ord('A')

        return chr((ord(c) - base_offset + shift) % 26 + base_offset)

    def gen_key(pt, key) -> Generator[Optional[int], None, None]:
        """Yields shift values corresponding to the key

        Key is converted to uppercase.
        Yields:
            The corresponding shift value for alphabetic characters,
            None for all others.
        """
        i, non_alphabetic = 0, 0
        key = key.upper()
        while i < len(pt):
            if not pt[i].isalpha():
                yield None
                non_alphabetic += 1
            else:
                index = (i - non_alphabetic) % len(key)
                yield ord(key[index]) - ord('A')
            i += 1

    def encrypt(pt, key):
        ct = []
        for c, k in zip(pt, Vigenere.gen_key(pt, key)):
            if k:
                ct.append(Vigenere.shift_char(c, k))
            else:
                ct.append(c)
        return "".join(ct)

    def decrypt(ct, key):
        pt = []
        for c, k in zip(ct, Vigenere.gen_key(ct, key)):
            if k:
                pt.append(Vigenere.shift_char(c, 26 - k))
            else:
                pt.append(c)
        return "".join(pt)

    def kasiski(ct: str, min_len=2) -> list[int]:
        candidates = defaultdict(int)
        for i in range(len(ct) - min_len):
            needle = ct[i:i+min_len]
            if (j := ct.find(needle, i + min_len)):
                candidates[j - i] += 1

KEY = "caesar"
ct = "Vhi Nixgnije tkplwr zu a tglpcltzasgtmu sldsxatlvisf czrhij. Ik ks e eoig sshhzutmuakgd zwrjkor gf kje Gsejcr gapygr, azitj uwws r uirylv uhmxt mclyw tf gngjygv tlw eevivw mvuseye. WNAK{yek_xikyy_nktl_at}"
assert "FLAG" in Vigenere.decrypt(ct, KEY)
