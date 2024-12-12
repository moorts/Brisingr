# Brisingr - My collection of cryptography stuff

## Dependencies
- pycryptodome (managed by uv)
- sagemath (managed by you)

## Elliptic Curves (`brisingr/curves`)

- TwistedEdwardsCurves

## RSA (`brisingr/rsa`)

Implemented attacks:
- Franklin-Reiter related message attack.
- Coppersmith's short-pad attack
- Wiener's Attack

## PRNGs (`brisingr/prngs`)

- Mersenne Twister

## Symmetric Ciphers (`brisingr/symmetric`)

Implemented Attacks:
- `brisingr/symmetric/block_cipher`
  - Padding Oracle
- `brisingr/symmetric/block_cipher`
  - Data structure for keeping track of impossible bytes.

## Utils (`brisingr/Utils`)

### Numbers

* precision cube root
* continuous fraction extension
