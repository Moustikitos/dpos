# -*- encoding:utf-8 -*-

from pySecp256k1 import sig
from dposlib.util.bin import unhexlify

sig._unhexlify = unhexlify
Signature = sig.Signature
