<a name="dposlib.blockchain"></a>
# dposlib.blockchain

<a name="dposlib.blockchain.isLinked"></a>
#### isLinked

```python
isLinked(func)
```

`Python decorator`.
First argument of decorated function have to be a `Content` or an
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

See [`dposlib.ark.v2.transfer`](v2.md#transfer).

<a name="dposlib.blockchain.Wallet.registerSecondSecret"></a>
#### registerSecondSecret

```python
 | @isLinked
 | registerSecondSecret(secondSecret)
```

See [`dposlib.ark.v2.registerSecondSecret`](
    v2.md#registersecondsecret
).

<a name="dposlib.blockchain.Wallet.registerSecondPublicKey"></a>
#### registerSecondPublicKey

```python
 | @isLinked
 | registerSecondPublicKey(secondPublicKey)
```

See [`dposlib.ark.v2.registerSecondPublicKey`](
    v2.md#registersecondpublickey
).

<a name="dposlib.blockchain.Wallet.registerAsDelegate"></a>
#### registerAsDelegate

```python
 | @isLinked
 | registerAsDelegate(username)
```

See [`dposlib.ark.v2.registerAsDelegate`](
    v2.md#registerasdelegate
).

<a name="dposlib.blockchain.Wallet.upVote"></a>
#### upVote

```python
 | @isLinked
 | upVote(*usernames)
```

See [`dposlib.ark.v2.upVote`](v2.md#upvote).

<a name="dposlib.blockchain.Wallet.downVote"></a>
#### downVote

```python
 | @isLinked
 | downVote(*usernames)
```

See [`dposlib.ark.v2.downVote`](v2.md#downvote).

<a name="dposlib.blockchain.cfg"></a>
# dposlib.blockchain.cfg

This module stores blockchain parameters:

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

<a name="dposlib.blockchain.serializer"></a>
# dposlib.blockchain.serializer

<a name="dposlib.blockchain.tx"></a>
# dposlib.blockchain.tx

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

