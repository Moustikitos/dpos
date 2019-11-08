# -*- encoding:utf-8 -*-
# TODO : raise exception for each return None

from . import *


def sign(msg, secret0, k=None, canonical=True):
    k = (rand_k() if not k else k) % n
    Q = G * k
    invk = pow(k, n-2, n)

    r = Q.x % n
    if r == 0: return None

    s = (invk * (int_from_bytes(msg) + int_from_bytes(secret0) * r)) % n
    if s == 0: return None
    if canonical and (s > (n//2)): s = n-s

    return der_from_sig(r, s)

def rfc6979_sign(msg, secret0, canonical=True):
    V = None
    for i in range(1, 10):
        k, V = rfc6979_k(msg, int_from_bytes(secret0), V)
        sig = sign(msg, secret0, k, canonical)
        if sig:
            return sig
    return None

def verify(msg, pubkey, sig):
    r, s = Signature.der_decode(sig)
    if r == None or r > n or s > n: return False

    h = int_from_bytes(msg)
    c = pow(s, n-2, n)

    u1G = G * ((h*c) % n)
    u2Q = point_mul(PublicKey.decode(pubkey), ((r*c) % n))
    GQ = u1G + u2Q

    return (GQ.x % n) == r
