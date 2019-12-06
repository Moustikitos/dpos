.. _snippets:

===============
 Code snippets
===============

Advanced Crypto
---------------

Public key is a point on ``secp256k1`` curve defined by the multiplication of a
scalar with the curve generator point. Scalar used in such a process is called
the private key.

>>> from dposlib.ark import secp256k1 as curve
>>> curve.G  # curve generator point
[55066263022277343669578718895168534326250603453777594175500187360389116729240, 32670510020758816978083085130507043184471273380659243275938904335757337482424]
>>> 12 * curve.G
[94111259592240215275188773285036844871058226277992966241101117022315524122714, 76870767327212528811304566602812752860184934880685532702451763239157141742375]

In this example, ``12`` is the private key. In Ark blockchain, private key is
an hexlified 32-bytes-length sequence. Public key is encoded as hex string. 

>>> from dposlib.util.bin import hexlify
>>> puk = hexlify((12 * curve.G).encode())
>>> puk
'03d01115d548e7561b15c38f004d734633687cf4419620095bc5b0f47070afe85a'
>>> prk = hexlify(secp256k1.bytes_from_int(12))
>>> prk
'000000000000000000000000000000000000000000000000000000000000000c'

You can use :mod:`dposlib.ark.sig` module to issue and check signatures.

>>> from dposlib.ark.sig import Signature 
>>> sig1 = Signature.ecdsa_rfc6979_sign("simple message", prk)  # ark-core <= 2.5
>>> hexlify(sig1.der)
'3045022100dcdf549f3904eaec24af8aff6fc790429d0ed98e2ec38919db85ffa23e80fb2902201018d303a10c589abfacfc8cd51514d93a5b1484b0c11049765857f2dd6caa1f'
>>> sig2 = Signature.b410_schnorr_sign("simple message", prk)  # ark-core >= 2.6
>>> hexlify(sig2.raw)
'5ed1dfd2923f8434bac014f4b0214f8e69730f9b9c7a859d05ec6897fc3e42d7171857d8a2c8bb18fb2358bd02baad85672e9efa79c603231ab876a1c22b133a'
>>> sig1.ecdsa_verify("simple message", puk)
True
>>> sig2.b410_schnorr_verify("simple message", puk)
True

Peer targeting / JSON API access
--------------------------------

:mod:`dposlib.rest` module provides easy way to target a specific peer when
sending a http request in blockchain network. You can also access whatever 
JSON API endpoint.

  .. note::
  	Public ip of http request emitter have to be white listed on targetted
  	peer.

>>> from dposlib import rest
>>> # no need to call rest.use directive...
>>> # https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=ARK&limit=365&toTS=1577833140
>>> data = rest.GET.data.histoday(
...    peer="https://min-api.cryptocompare.com", fsym="BTC", tsym="ARK",
...    limit=365, toTs=1577833140
...)
>>> data["Data"][-1]
{u'volumeto': 242439.09, u'high': 42955.33, u'low': 40832.99, u'time': 1575072000, u'volumefrom': 5.761, u'close': 42789.9, u'open': 40966.82}
>>> # get configuration of https://explorer.ark.io:8443 peer
>>> data = rest.GET.api.node.configuration(peer="https://explorer.ark.io:8443")
>>> data["data"]["transactionPool"]
{u'dynamicFees': {u'minFeePool': 3000, u'minFeeBroadcast': 3000, u'enabled': True, u'addonBytes': {u'ipfs': 250, u'transfer': 100, u'timelockTransfer': 500, u'multiSignature':
500, u'delegateRegistration': 400000, u'delegateResignation': 100, u'multiPayment': 500, u'vote': 100, u'secondSignature': 250}}}>>> rest.use("ark")

Emoji in ``vendorField``
------------------------

This transaction will show a nice sparkle in its ``vendorField``:

>>> dposlib.core.transfer(1, "DChFFe4QMwZesdMYNEkJsqnqY4MnF4TYQu", vendorField=u"message with sparkles \u2728")
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "DChFFe4QMwZesdMYNEkJsqnqY4MnF4TYQu",
  "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
  "timestamp": 85040681,
  "type": 0,
  "vendorField": "message with sparkles \u2728",
  "version": 1
}

Emoji can be embeded in transaction ``vendorField`` using python unicode
string. For example:

  * |sparkles|: unicode hex value ``2728``, use ``\uXXXX`` format
>>> u"emoji defined by less than or equal 4 digits : \u2728 - "

  * |exchange|: unicode hex value ``1f4b1``, use ``\UXXXXXXXX`` format
>>> u"emoji defined by more than 4 digits : \U0001f4b1"

Multisignature server
---------------------

>>> import dposlib
>>> from dposlib import rest
>>> from mssrv import client
>>> rest.use("dark")
True
>>> client.API_PEER = "http://127.0.0.1:5000"
>>> t = dposlib.core.transfer(1, "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk", u"ms-srv test #4 \u2728", version=2)
>>> t.senderPublicKey = "02cccf1a186bed2cf8d22f6c46d8497a4eceeb8e159bde4ee83b908145764da5e3"
>>> t.setFee()
>>> client.postNewTransactions("dark", t)
{u'success': [u'transaction #1 successfully posted (id:7c01e5bd9d78a82f766db50c345cbcd227e47089b3fbeca7cde530a46bfcb77e)']}
>>> client.remoteSignWithSecret("dark", t.senderPublicKey, "7c01e5bd9d78a82f766db50c345cbcd227e47089b3fbeca7cde530a46bfcb77e")
secret >
{u'success': u'signature added to transaction'}
>>> client.remoteSignWithSecret("dark", t.senderPublicKey, "7c01e5bd9d78a82f766db50c345cbcd227e47089b3fbeca7cde530a46bfcb77e")
secret >
{u'broadcast': [u'47b7d0431a2996c04292ae9bddad36db52e3babcc666704d593da616ab6c207e'], u'accept': [u'47b7d0431a2996c04292ae9bddad36db52e3babcc666704d593da616ab6c207e'], u'invalid': [], u'excess': []}
