<a name="dposlib.ark.v2"></a>
# dposlib.ark.v2

<a name="dposlib.ark.v2.init"></a>
#### init

```python
init(seed=None)
```

Blockchain initialisation. It stores root values in [`rest.cfg`](
    network.md#rest
) modules.

<a name="dposlib.ark.v2.stop"></a>
#### stop

```python
stop()
```

Stop daemon initialized by [`init`](blockchain.md#init) call.

<a name="dposlib.ark.v2.transfer"></a>
#### transfer

```python
transfer(amount, address, vendorField=None, expiration=0)
```

Build a transfer transaction. Emoji can be included in transaction
vendorField using unicode formating.


```python
>>> u"message with sparkles \u2728"
```

**Arguments**:

- `amount` _float_ - transaction amount in ark
- `address` _str_ - valid recipient address
- `vendorField` _str_ - vendor field message
- `expiration` _float_ - time of persistance in hour

**Returns**:

  transaction object

<a name="dposlib.ark.v2.registerSecondSecret"></a>
#### registerSecondSecret

```python
registerSecondSecret(secondSecret)
```

Build a second secret registration transaction.

**Arguments**:

- `secondSecret` _str_ - passphrase

**Returns**:

  transaction object

<a name="dposlib.ark.v2.registerSecondPublicKey"></a>
#### registerSecondPublicKey

```python
registerSecondPublicKey(secondPublicKey)
```

Build a second secret registration transaction.

*You must own the secret issuing secondPublicKey*

**Arguments**:

- `secondPublicKey` _str_ - public key as hex string

**Returns**:

  transaction object

<a name="dposlib.ark.v2.registerAsDelegate"></a>
#### registerAsDelegate

```python
registerAsDelegate(username)
```

Build a delegate registration transaction.

**Arguments**:

- `username` _str_ - delegate username

**Returns**:

  transaction object

<a name="dposlib.ark.v2.upVote"></a>
#### upVote

```python
upVote(*usernames)
```

Build an upvote transaction.

**Arguments**:

- `usernames` _iterable_ - delegate usernames as str
  iterable

**Returns**:

  transaction object

<a name="dposlib.ark.v2.downVote"></a>
#### downVote

```python
downVote(*usernames)
```

Build a downvote transaction.

**Arguments**:

- `usernames` _iterable_ - delegate usernames as str
  iterable

**Returns**:

  transaction object

<a name="dposlib.ark.v2.registerMultiSignature"></a>
#### registerMultiSignature

```python
registerMultiSignature(minSig, *publicKeys)
```

Build a multisignature registration transaction.

**Arguments**:

- `minSig` _int_ - minimum signature required
- `publicKeys` _list of str_ - public key list

**Returns**:

  transaction object

<a name="dposlib.ark.v2.registerIpfs"></a>
#### registerIpfs

```python
registerIpfs(ipfs)
```

Build an IPFS registration transaction.

**Arguments**:

- `ipfs` _str_ - ipfs DAG

**Returns**:

  transaction object

<a name="dposlib.ark.v2.multiPayment"></a>
#### multiPayment

```python
multiPayment(*pairs, **kwargs)
```

Build multi-payment transaction. Emoji can be included in transaction
vendorField using unicode formating.


```python
>>> u"message with sparkles \u2728"
```

**Arguments**:

- `pairs` _iterable_ - recipient-amount pair iterable
- `vendorField` _str_ - vendor field message

**Returns**:

  transaction object

<a name="dposlib.ark.v2.delegateResignation"></a>
#### delegateResignation

```python
delegateResignation()
```

Build a delegate resignation transaction.

**Returns**:

  transaction object

<a name="dposlib.ark.v2.htlcSecret"></a>
#### htlcSecret

```python
htlcSecret(secret)
```

Compute an HTLC secret hex string from passphrase.

**Arguments**:

- `secret` _str_ - passphrase

**Returns**:

  transaction object

<a name="dposlib.ark.v2.htlcLock"></a>
#### htlcLock

```python
htlcLock(amount, address, secret, expiration=24, vendorField=None)
```

Build an HTLC lock transaction. Emoji can be included in transaction
vendorField using unicode formating.


```python
>>> u"message with sparkles \u2728"
```

**Arguments**:

- `amount` _float_ - transaction amount in ark
- `address` _str_ - valid recipient address
- `secret` _str_ - lock passphrase
- `expiration` _float_ - transaction validity in hour
- `vendorField` _str_ - vendor field message

**Returns**:

  transaction object

<a name="dposlib.ark.v2.htlcClaim"></a>
#### htlcClaim

```python
htlcClaim(txid, secret)
```

Build an HTLC claim transaction.

**Arguments**:

- `txid` _str_ - htlc lock transaction id
- `secret` _str_ - passphrase used by htlc lock transaction

**Returns**:

  transaction object

<a name="dposlib.ark.v2.htlcRefund"></a>
#### htlcRefund

```python
htlcRefund(txid)
```

Build an HTLC refund transaction.

**Arguments**:

- `txid` _str_ - htlc lock transaction id

**Returns**:

  transaction object

<a name="dposlib.ark.v2.api"></a>
# dposlib.ark.v2.api

<a name="dposlib.ark.v2.api.Wallet"></a>
## Wallet Objects

```python
class Wallet(dposlib.blockchain.Wallet)
```

<a name="dposlib.ark.v2.api.Wallet.registerIpfs"></a>
#### registerIpfs

```python
 | @dposlib.blockchain.isLinked
 | registerIpfs(ipfs)
```

See [`dposlib.ark.v2.registerIpfs`](blockchain.md#registeripfs).

<a name="dposlib.ark.v2.api.Wallet.multiSend"></a>
#### multiSend

```python
 | @dposlib.blockchain.isLinked
 | multiSend(*pairs, **kwargs)
```

See [`dposlib.ark.v2.multiPayment`](blockchain.md#multipayment).

<a name="dposlib.ark.v2.api.Wallet.resignate"></a>
#### resignate

```python
 | @dposlib.blockchain.isLinked
 | resignate()
```

See [`dposlib.ark.v2.delegateResignation`](blockchain.md#resignate).

<a name="dposlib.ark.v2.api.Wallet.sendHtlc"></a>
#### sendHtlc

```python
 | @dposlib.blockchain.isLinked
 | sendHtlc(amount, address, secret, expiration=24, vendorField=None)
```

See [`dposlib.ark.v2.htlcLock`](blockchain.md#sendhtlc).

<a name="dposlib.ark.v2.api.Wallet.claimHtlc"></a>
#### claimHtlc

```python
 | @dposlib.blockchain.isLinked
 | claimHtlc(txid, secret)
```

See [`dposlib.ark.v2.htlcClaim`](blockchain.md#claimhtlc).

<a name="dposlib.ark.v2.api.Wallet.refundHtlc"></a>
#### refundHtlc

```python
 | @dposlib.blockchain.isLinked
 | refundHtlc(txid)
```

See [`dposlib.ark.v2.htlcRefund`](blockchain.md#refundhtlc).

<a name="dposlib.blockchain"></a>
# dposlib.blockchain

<a name="dposlib.blockchain.isLinked"></a>
#### isLinked

```python
isLinked(func)
```

`Python decorator`.
First argument of decorated function  have to be a `Content` or an
object containing a valid `address`, `_derivationPath` or `publicKey`
attribute. It executes the decorated `function` if the object is correctly
linked using [`dposlib.blockchain.link`](blockchain.md#link) definition.

<a name="dposlib.blockchain.link"></a>
#### link

```python
link(cls, secret=None, secondSecret=None)
```

Associates crypto keys into a `dposlib.blockchain.Content` object according
to secrets. If `secret` or `secondSecret` are not `str`, they are
considered as `None`.

**Arguments**:

- `cls` _Content_ - content object
- `secret` _str_ - secret string
- `secondSecret` _str_ - second secret string

**Returns**:

  True if secret and second secret match

<a name="dposlib.blockchain.unLink"></a>
#### unLink

```python
unLink(cls)
```

Remove crypto keys association.

<a name="dposlib.blockchain.JSDict"></a>
## JSDict Objects

```python
class JSDict(dict)
```

Read only dictionary with js object behaviour.

```python
>>> jsdic = blockchain.JSDict(value=5)
>>> jsdic
{'value': 5}
>>> jsdic.value
5
```

<a name="dposlib.blockchain.Content"></a>
## Content Objects

```python
class Content(object)
```

Live object connected to blockchain. It is initialized with
`dposlib.rest.GET` request. Object is updated every 30s. Endpoint response
can be a `dict` or a `list`. If it is a `list`, it is stored in `data`
attribute else all fields are stored as instance attribute.

```python
>>> txs = blockchain.Content(rest.GET.api.transactions)
>>> txs.data[0]["timestamp"]
{
    'epoch': 121912776,
    'unix': 1612013976,
    'human': '2021-01-30T13:39:36.000Z'
}
>>> tx = blockchain.Content(
    rest.GET.api.transactions,
    "d36a164a54df9d1c7889521ece15318d6945e9971fecd0a96a9c18e74e0adbf9",
)
>>> tx.timestamp
{
    'epoch': 121919704,
    'unix': 1612020904,
    'human': '2021-01-30T15:35:04.000Z'
}
>>> tx.amount
212963052
>>> tx.datetime
datetime.datetime(2021, 1, 30, 15, 35, 4, tzinfo=<UTC>)
```

<a name="dposlib.blockchain.Content.datetime"></a>
#### datetime

if timestamp attributes exists, return associated python datetime object

<a name="dposlib.blockchain.Wallet"></a>
## Wallet Objects

```python
class Wallet(Content)
```

**Arguments**:

- `fee` _int or str_ - set fee level as `fee multiplier` integer or one of
  `minFee`, `avgFee`, `maxFee` string
- `fee_included` _bool_ - set to True if amout + fee is the total desired
  out flow

<a name="dposlib.blockchain.Wallet.delegate"></a>
#### delegate

return delegate attributes if wallet is registered as delegate

<a name="dposlib.blockchain.Wallet.username"></a>
#### username

return delegate username if wallet is registered as delegate

<a name="dposlib.blockchain.Wallet.secondPublicKey"></a>
#### secondPublicKey

return second public key if second signature is set to wallet

<a name="dposlib.blockchain.Wallet.send"></a>
#### send

```python
 | @isLinked
 | send(amount, address, vendorField=None)
```

See [`dposlib.ark.v2.transfer`](blockchain.md#send).

<a name="dposlib.blockchain.Wallet.registerSecondSecret"></a>
#### registerSecondSecret

```python
 | @isLinked
 | registerSecondSecret(secondSecret)
```

See [`dposlib.ark.v2.registerSecondSecret`](
    blockchain.md#registersecondsecret
).

<a name="dposlib.blockchain.Wallet.registerSecondPublicKey"></a>
#### registerSecondPublicKey

```python
 | @isLinked
 | registerSecondPublicKey(secondPublicKey)
```

See [`dposlib.ark.v2.registerSecondPublicKey`](
    blockchain.md#registersecondpublickey
).

<a name="dposlib.blockchain.Wallet.registerAsDelegate"></a>
#### registerAsDelegate

```python
 | @isLinked
 | registerAsDelegate(username)
```

See [`dposlib.ark.v2.registerAsDelegate`](
    blockchain.md#registerasdelegate
).

<a name="dposlib.blockchain.Wallet.upVote"></a>
#### upVote

```python
 | @isLinked
 | upVote(*usernames)
```

See [`dposlib.ark.v2.upVote`](blockchain.md#upvote).

<a name="dposlib.blockchain.Wallet.downVote"></a>
#### downVote

```python
 | @isLinked
 | downVote(*usernames)
```

See [`dposlib.ark.v2.downVote`](blockchain.md#downvote).

<a name="dposlib.blockchain.cfg"></a>
# dposlib.blockchain.cfg

This module stores blockchain parameters.

  * activeDelegates:
  * aip20:
  * begintime:
  * blockreward:
  * blocktime:
  * broadcast:
  * doffsets:
  * explorer:
  * familly:
  * fees:
  * feestats:
  * headers:
  * hotmode:
  * marker:
  * maxTransactions:
  * maxvote:
  * maxvotepertx:
  * network:
  * peers:
  * ports:
  * pubkeyHash:
  * slip44:
  * symbol:
  * timeout:
  * token:
  * txversion:
  * version:
  * wif:

<a name="dposlib.blockchain.tx"></a>
# dposlib.blockchain.tx

<a name="dposlib.blockchain.tx.computeDynamicFees"></a>
#### computeDynamicFees

```python
computeDynamicFees(tx, FMULT=None)
```

Compute transaction fees according to [AIP 16 ](
https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-16.md
).

**Arguments**:

- `tx` _dict or Transaction_ - transaction object

**Returns**:

  fees

<a name="dposlib.blockchain.tx.setFeeIncluded"></a>
#### setFeeIncluded

```python
setFeeIncluded(cls)
```

Arrange `amount` and `fee` values so the total `arktoshi` flow is
the desired spent.

<a name="dposlib.blockchain.tx.unsetFeeIncluded"></a>
#### unsetFeeIncluded

```python
unsetFeeIncluded(cls)
```

Arrange `amount` and `fee` values so the total `arktoshi` flow is
the desired spent plus the fee.

<a name="dposlib.blockchain.tx.serialize"></a>
#### serialize

```python
serialize(tx, **options)
```

Serialize transaction.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object

**Returns**:

  bytes sequence

<a name="dposlib.blockchain.tx.Transaction"></a>
## Transaction Objects

```python
class Transaction(dict)
```

A python `dict` that implements all the necessities to manually
generate valid transactions.

<a name="dposlib.blockchain.tx.Transaction.feeIncluded"></a>
#### feeIncluded

use feeIncluded option

<a name="dposlib.blockchain.tx.Transaction.useDynamicFee"></a>
#### useDynamicFee

```python
 | @staticmethod
 | useDynamicFee(value="minFee")
```

Activate and configure dynamic fees parameters. Value can be either an
integer defining the fee multiplier constant or a string defining the
fee level to use acccording to the 30-days-average. possible values are
`avgFee` `minFee` (default) and `maxFee`.

**Arguments**:

- `value` _str or int_ - constant or fee multiplier

<a name="dposlib.blockchain.tx.Transaction.link"></a>
#### link

```python
 | link(secret=None, secondSecret=None)
```

Save public and private keys derived from secrets. This is equivalent
to wallet login. it limits number of secret keyboard entries.

**Arguments**:

- `secret` _str_ - passphrase
- `secondSecret` _str_ - second passphrase

<a name="dposlib.blockchain.tx.Transaction.setFee"></a>
#### setFee

```python
 | setFee(value=None)
```

Set `fee` field manually or according to inner parameters.

**Arguments**:

- `value` _int_ - fee value in `arktoshi` to set manually

<a name="dposlib.blockchain.tx.Transaction.sign"></a>
#### sign

```python
 | sign()
```

Generate the `signature` field. Private key have to be set first. See
[`link`](blockchain.md#link_1).

<a name="dposlib.blockchain.tx.Transaction.signSign"></a>
#### signSign

```python
 | signSign()
```

Generate the `signSignature` field. Transaction have to be signed and
second  private key have to be set first. See [`link`](
    blockchain.md#link_1
).

<a name="dposlib.blockchain.tx.Transaction.signWithSecret"></a>
#### signWithSecret

```python
 | signWithSecret(secret)
```

Generate the `signature` field using passphrase. The associated
public and private keys are stored till [`unlink`](
blockchain.md#unlink
) is called.

**Arguments**:

- `secret` _`str`_ - passphrase

<a name="dposlib.blockchain.tx.Transaction.signSignWithSecondSecret"></a>
#### signSignWithSecondSecret

```python
 | signSignWithSecondSecret(secondSecret)
```

Generate the `signSignature` field using second passphrase. The
associated second public and private keys are stored till [`unlink`](
blockchain.md#unlink
) is called.

**Arguments**:

- `secondSecret` _`str`_ - second passphrase

<a name="dposlib.blockchain.tx.Transaction.multiSignWithSecret"></a>
#### multiSignWithSecret

```python
 | multiSignWithSecret(secret)
```

Add a signature in `signatures` field.

**Arguments**:

- `index` _int_ - signature index
- `secret` _str_ - passphrase

<a name="dposlib.blockchain.tx.Transaction.signWithKeys"></a>
#### signWithKeys

```python
 | signWithKeys(publicKey, privateKey)
```

Generate the `signature` field using public and private keys. They
are till [`unlink`](blockchain.md#unlink) is called.

**Arguments**:

- `publicKey` _str_ - public key as hex string
- `privateKey` _str_ - private key as hex string

<a name="dposlib.blockchain.tx.Transaction.signSignWithKey"></a>
#### signSignWithKey

```python
 | signSignWithKey(secondPrivateKey)
```

Generate the `signSignature` field using second private key. It is
stored till [`unlink`](blockchain.md#unlink) is called.

**Arguments**:

- `secondPrivateKey` _`str`_ - second private key as hex string

<a name="dposlib.blockchain.tx.Transaction.multiSignWithKey"></a>
#### multiSignWithKey

```python
 | multiSignWithKey(privateKey)
```

Add a signature in `signatures` field according to given index and
privateKey.

**Arguments**:

- `privateKey` _str_ - private key as hex string

<a name="dposlib.blockchain.tx.Transaction.identify"></a>
#### identify

```python
 | identify()
```

Generate the `id` field. Transaction have to be signed.

<a name="dposlib.blockchain.tx.Transaction.finalize"></a>
#### finalize

```python
 | finalize(secret=None, secondSecret=None, fee=None, fee_included=False)
```

Finalize a transaction by setting `fee`, signatures and `id`.

**Arguments**:

- `secret` _str_ - passphrase
- `secondSecret` _str_ - second passphrase
- `fee` _int_ - manually set fee value in `satoshi`
- `fee_included` _bool_ - see [`Transaction.feeIncluded`](
  blockchain.md#feeincluded
  )

