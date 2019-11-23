=============================
 dposlib: Ark API for Humans
=============================

Release v\ |version| - (:ref:`Installation <install>`)

.. image:: https://pepy.tech/badge/dposlib/week
    :target: https://pepy.tech/project/dposlib/week

.. image:: https://img.shields.io/pypi/v/dposlib.svg
    :target: https://pypi.python.org/pypi/dposlib

.. image:: https://readthedocs.org/projects/dpos/badge/?version=latest
    :target: https://dpos.readthedocs.io/en/latest/?badge=latest

.. image:: https://travis-ci.com/Moustikitos/dpos.svg?branch=master
    :target: https://travis-ci.com/Moustikitos/dpos

.. image:: https://img.shields.io/pypi/pyversions/dposlib.svg
    :target: https://pypi.python.org/pypi/dposlib

``dposlib`` is a simple  package providing efficient API to interact with Ark
blockchain and its forks. It is designed to run with both python 2 and 3.

Simplicity of ``REST`` API::

    >>> from dposlib import rest
    >>> # ~ https://explorer.ark.io:8443/api/delegates/arky
    >>> rest.GET.api.delegates.arky(peer="https://explorer.ark.io:8443")
    {u'data': {u'username': u'arky', u'votes': u'172572088664599', u'blocks': {u'produced': 199859, u'last': {u'timestamp': {u'epoch': 84182056, u'unix': 1574283256, u'human': u'2019-11-20T20:54:16.000Z'}, u'id': u'5f5f9897f8fca2a5600ace0d75d67811c67df8111a7deea13d7d6b2c532fae43', u'height': 10380869}}, u'rank': 11, u'publicKey': u'030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d60a15e9', u'production': {u'approval': 1.35}, u'forged': {u'total': u'40118247659340', u'rewards': u'39687400000000', u'fees': u'430847659340'}, u'address': u'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE'}}
    >>> # using returnKey arktoshi values are converted to ark
    >>> rest.GET.api.transactions(peer="https://explorer.ark.io:8443", returnKey="data")[0]
    {u'fee': 0.00816, u'type': 0, u'sender': u'AKATy581uXWrbm8B4DTQh4R9RbqaWRiKRY', u'timestamp': {u'epoch': 84182307, u'unix': 1574283507, u'human': u'2019-11-20T20:58:27.000Z'}, u'blockId': u'a1b305a87217c2f622a922a97a778c677f7dbd23031dae42e3b494883b855a70', u'vendorField': u'Payout from arkmoon', u'senderPublicKey': u'0232b96d57ac27f9a99242bc886e433baa89f596d435153c9dae47222c0d1cecc3', u'amount': 20.52064264, u'version': 1, u'signSignature': u'304402200ac41802f33a5f377975efc9ebf39a666a9d76c2facb8773783289df7f6a9cd302206c5d2aed3359d3858fb3f4d5fc2a76952eb518cf9d242bb91fd11c0801e4ea4e', u'confirmations': 21, u'signature': u'3045022100dc6dbaa4b056f10268b587da290900725246e3239df1fa3e3c53445da36f03ee02206d57bbdff6d7f9ebca719a41112f23128f1a84161dd82597d63351e3c4d868b0', u'recipient': u'AXPLW2TzBsXcPiaeVGBSELEAXj4RPaWNjB', u'id': u'efeab09925c3347b4a18854a9192d7d722ee32850a7bf91d57628cb77714192e'}
    >>> # peer keyword is not mandatory when a blockchain is linked using rest.use directive
    >>> rest.use("ark")
    >>> # ~ GET /api/blocks endpoint
    >>> rest.GET.api.blocks(returnKey="data")[0]
    {u'payload': {u'length': 0, u'hash': u'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}, u'generator': {u'username': u'arkmoon', u'publicKey': u'0232b96d57ac27f9a99242bc886e433baa89f596d435153c9dae47222c0d1cecc3', u'address': u'AKATy581uXWrbm8B4DTQh4R9RbqaWRiKRY'}, u'transactions': 0, u'timestamp': {u'epoch': 84183376, u'unix': 1574284576, u'human': u'2019-11-20T21:16:16.000Z'}, u'height': 10381034, u'version': 0, u'forged': {u'fee': 0.0, u'amount': 0.0, u'total': 2.0, u'reward': 2.0}, u'confirmations': 1, u'signature': u'3045022100a8b6b48c0094f9c84b7da5ae457ca33d5ba0d9a3df963c1e17c42cb52fb563a9022020ea96cf76529943b03b864bbb722352ef6faf5701e36bc16f9903ec2234309b', u'id': u'd2e042495ab64e7cf5bb0fc8d4ce6972a98f29a56d960b707f3c6abd2791a5e2', u'previous': u'ea1b7082424592545860a671a77ef7f59c3730665208080d2481e363be6c1ed0'}

``ECDSA`` and ``SCHNORR`` signatures can be performed using
``dposlib.ark.sig`` and ``dposlib.ark.crypto`` modules::

    >>> import dposlib.ark.sig as sig
    >>> import dposlib.ark.crypto as crypto
    >>> keys = crypto.getKeys("secret")
    >>> keys
    {'publicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933', 'privateKey': '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b', 'wif': 'SB3BGPGRh1SRuQd52h7f5jsHUg1G9ATEvSeA7L5Bz4qySQww4k7N'}
    >>> s = sig.Signature.ecdsa_sign("simple message", keys["privateKey"])
    >>> s
    [35314084229303150913836520313684788872375048130620231441581098465861064088693, 46834985432572711527816757766911460691200906216722908963407150983007804769398]
    >>> s.der
    b"0D\x02 N\x13\x108J\xd0\xd6\xff\x80'\xf2\xf8`\xd6(\xb2\xa6@\x03\x0bF#\xa3\x93\xe1\xdf&\xf7\xdd\xce\\u\x02 g\x8b\xa9\x90V\xaa\xdf\xa7\xf2-;z\xa5.D\x8bq8ehG\xb7\x11\x07-`\xd2\xd9\xd3.\xc4v"
    >>> crypto.hexlify(s.der)
    '3044022041e5aa3da79523a2b342180cb7c04056f8f02e005ea6ec1f14094c66d692f04402200261177cdd88525249a0619d6009adbc6681c250c83748c0cde611f21f543008'
    >>> crypto.hexlify(s.raw)
    '4e1310384ad0d6ff8027f2f860d628b2a640030b4623a393e1df26f7ddce5c75678ba99056aadfa7f22d3b7aa52e448b7138656847b711072d60d2d9d32ec476'
    >>> crypto.hexlify(sig.Signature.schnorr_sign("simple message", keys["privateKey"]).raw)
    '5fbb0bb00b043400e1fc435c867c738ac80d2c268cd2d61616785315ad330c884a3cfb50bf0da8de9021d42ce2139b6b6547d2bcd884a2da7f5c2e9bfb9cb206'

``dposlib.ark.v2`` package provides :class:`dposlib.blockchain.Transaction` 
class and its associated builders::

    >>> from dposlib import rest
    >>> rest.use("d.ark")
    True
    >>> from dposlib.ark.v2 import *
    >>> tx = transfer(1, "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk", u"simple message with sparkle \u2728", version=2)
    >>> tx.finalize("first secret", "second secret")
    >>> tx
    {
        "amount": 100000000,
        "asset": {},
        "expiration": 0,
        "fee": 4013642,
        "id": "041ad1e3dd06d29ef59b2c7e19fea4ced0e7fcf9fdc22edcf26e5cc016e10f38",
        "network": 30,
        "nonce": 377,
        "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
        "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
        "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
        "signSignature": "3d29356c77b63c2d6ce679dad95961b40ea606823bf729a158df5c8378c79c5588ad675ee147a7f77b18518c5bdf9b1a73567d72c3af0bfbe22043b9e1a95e6f",
        "signature": "871ac31e7bad08b684b27f1b8a4b9f9f760bb32d1d36cc03e03872edc6070f8d9fec2621ea87e2ea0ae7750e0e7a5db52f39b32e05af76a4331a92e17dbe9f4a",
        "timestamp": 84186531,
        "type": 0,
        "typeGroup": 1,
        "vendorField": "simple message with sparkle \u2728",
        "version": 2
    }
    >>> broadcastTransactions(tx)
    {u'data': {u'broadcast': [u'041ad1e3dd06d29ef59b2c7e19fea4ced0e7fcf9fdc22edcf26e5cc016e10f38'], u'invalid': [], u'accept': [u'041ad1e3dd06d29ef59b2c7e19fea4ced0e7fcf9fdc22edcf26e5cc016e10f38'], u'excess': []}}

`See the transaction in devnet explorer <https://dexplorer.ark.io/transaction/041ad1e3dd06d29ef59b2c7e19fea4ced0e7fcf9fdc22edcf26e5cc016e10f38>`_

-------------------------------------------------------------------------------

.. toctree::
    :maxdepth: 2
    :hidden:

    install
    secp256k1
    rest
    core
    api
    snippets
