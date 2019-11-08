# -*- encoding:utf-8 -*-

from . import *


# https://github.com/bcoin-org/bcrypto/blob/v4.1.0/lib/js/schnorr.js
def bcrypto410_sign(msg, seckey0):
    if len(msg) != 32:
        raise ValueError('The message must be a 32-byte array.')

    seckey = int_from_bytes(seckey0)
    if not (1 <= seckey <= n - 1):
        raise ValueError('The secret key must be an integer in the range 1..n-1.')

    k0 = int_from_bytes(hash_sha256(seckey0 + msg)) % n
    if k0 == 0:
        raise RuntimeError('Failure. This happens only with negligible probability.')

    R = G * k0
    Rraw = bytes_from_int(R.x)
    e = int_from_bytes(hash_sha256(Rraw + encoded_from_point(G*seckey) + msg)) % n

    seckey %= n
    k0 %= n
    k = n - k0 if not is_quad(R.y) else k0

    s = (k + e * seckey) % n
    s %= n

    return Rraw + bytes_from_int(s)

def bcrypto410_verify(msg, pubkey, sig):
    if len(msg) != 32:
        raise ValueError('The message must be a 32-byte array.')
    if len(sig) != 64:
        raise ValueError('The signature must be a 64-byte array.')

    P = PublicKey.decode(pubkey)
    r, s = Signature.raw_decode(sig)
    if r >= p or s >= n: return False

    e = int_from_bytes(hash_sha256(sig[0:32] + pubkey + msg)) % n
    R = Point(*(G*s + point_mul(P, n-e))) # P*(n-e) does not work...
    if R is None or not is_quad(R.y) or R.x != r:
        return False

    return True

def bytes_from_point(P):
    return bytes_from_int(x(P))

def point_from_bytes(b):
    x = int_from_bytes(b)
    y_sq = (pow(x, 3, p) + 7) % p
    y = pow(y_sq, (p + 1) // 4, p)
    if pow(y, 2, p) != y_sq:
        return None
    return [x, y]

def sign(msg, seckey0):
    if len(msg) != 32:
        raise ValueError('The message must be a 32-byte array.')

    seckey0 = int_from_bytes(seckey0)
    if not (1 <= seckey0 <= n - 1):
        raise ValueError('The secret key must be an integer in the range 1..n-1.')

    P = G*seckey0
    seckey = seckey0 if is_quad(P.y) else n - seckey0

    k0 = int_from_bytes(tagged_hash("BIPSchnorrDerive", bytes_from_int(seckey) + msg)) % n
    if k0 == 0:
        raise RuntimeError('Failure. This happens only with negligible probability.')

    R = G*k0
    k = n - k0 if not is_quad(R.y) else k0
    r = bytes_from_point(R)
    e = int_from_bytes(tagged_hash("BIPSchnorr", r + bytes_from_point(P) + msg)) % n

    return r + bytes_from_int((k + e * seckey) % n)

def verify(msg, pubkey, sig):
    if len(msg) != 32:
        raise ValueError('The message must be a 32-byte array.')
    if len(pubkey) != 32:
        raise ValueError('The public key must be a 32-byte array.')
    if len(sig) != 64:
        raise ValueError('The signature must be a 64-byte array.')

    P = point_from_bytes(pubkey)
    if (P is None):
        return False

    r, s = Signature.raw_decode(sig)
    if (r >= p or s >= n):
        return False

    e = int_from_bytes(tagged_hash("BIPSchnorr", sig[0:32] + pubkey + msg)) % n
    R = Point(*(G*s + point_mul(P, n-e))) # P*(n-e) does not work...
    if R is None or not is_quad(R.y) or R.x != r:
        return False

    return True
