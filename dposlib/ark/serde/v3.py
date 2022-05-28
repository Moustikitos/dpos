# -*- coding: utf-8 -*-

from dposlib.util.bin import unhexlify, hexlify, pack, pack_bytes


# solar vote transaction
def _1_3(tx, buf):
    asset = tx.get("asset", {})
    usernames = asset.get("votes", False)
    if usernames:
        pack("<B", buf, (len(usernames), ))
        for username in usernames:
            pack_bytes(buf, unhexlify(
                ("%02x" % len(username)) +
                ("01" if username.startswith("+") else "00") +
                hexlify(username[1:])
            ))
    else:
        raise Exception("no up/down vote given")


# solar-network burn transaction
def _2_0(tx, buf):
    dict.__setitem__(tx, "fee", 0)
    pack("<Q", buf, (int(tx.get("amount", 0)), ))
