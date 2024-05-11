from copy import deepcopy


class ExclusionTable:
    """An abstraction over inequality oracles.

    Which is what I call it when a server disallows specific bytes to show up
    in the ciphertext or key.

    The classic example is that the server does not allow the key in a
    stream cipher to contain the zero byte. In this scenario, you can
    recover the key by keeping track of the values the ciphertexts took.
    Once you accumulate enough ciphertexts, there will remain only one possible
    byte for each byte of the key.

    This class does the keeping track.
    """

    def __init__(self, len_secret: int, alphabet: bytes = None):
        possible_bytes = set(range(256))
        if alphabet:
            possible_bytes = set(bytes)

        self.len_secret = len_secret
        self.valid_bytes = [deepcopy(possible_bytes) for _ in range(len_secret)]
        self.plaintext = [None] * len_secret
        self.plaintext_bytes_recovered = 0

    def get_plaintext(self):
        pt = b""
        for byte in self.plaintext:
            if byte:
                pt += bytes([byte])
            else:
                pt += b"#"
        return pt

    def add_invalid_ciphertext(self, ct: bytes) -> bool:
        for i, byte in enumerate(ct):
            if self.plaintext[i]:
                continue

            self.add_invalid_byte(i, byte)

        return self.plaintext_bytes_recovered == self.len_secret

    def add_invalid_byte(self, index: int, byte: int) -> bool:
        valid_bytes_i = self.valid_bytes[index]

        valid_bytes_i.discard(byte)
        if len(valid_bytes_i) == 1:
            self.plaintext[index] = list(valid_bytes_i)[0]
            self.plaintext_bytes_recovered += 1

