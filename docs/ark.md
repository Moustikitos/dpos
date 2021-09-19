<a name="dposlib.ark"></a>
# dposlib.ark

<a name="dposlib.ark.Content"></a>
## Content Objects

```python
class Content(object)
```

Live object connected to blockchain. It is initialized with
`dposlib.rest.GET` request. Object is updated every 30s. Endpoint response
can be a `dict` or a `list`. If it is a `list`, it is stored in `data`
attribute else all fields are stored as instance attribute.


```python
>>> txs = dposlib.ark.Content(rest.GET.api.transactions)
>>> txs.data[0]["timestamp"]
{
    'epoch': 121912776,
    'unix': 1612013976,
    'human': '2021-01-30T13:39:36.000Z'
}
>>> tx = dposlib.ark.Content(
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

**Arguments**:

- `ndpt` _usrv.req.Endpoint_ - endpoint class to be called.
- `*args` - Variable length argument list used by `usrv.req.Endpoint`.
  
  **Kwargs**:
  
  * `keep_alive` *bool* - set hook to update data from blockcahin. Default
  to True.

<a name="dposlib.ark.Content.filter"></a>
#### filter

```python
 | filter(data)
```

Convert data as JSDict object converting string values in int if
possible.

<a name="dposlib.ark.Wallet"></a>
## Wallet Objects

```python
class Wallet(Content)
```

Wallet root class that implements basic wallet behaviour.

**Arguments**:

- `ndpt` _usrv.req.Endpoint_ - endpoint class to be called.
- `*args` - Variable length argument list used by `dposlib.ark.Content`.
- `**kwargs` - Variable key argument used by `dposlib.ark.Content`.
  
  **Specific kwargs**:
  
  * `keep_alive` *bool* - automatic update data from blockcahin. Default
  to True.
  * `fee` *int or str* - set fee level as fee multiplier string value or
  one of **minFee**, **avgFee**, **maxFee**. Default to **avgFee**.
  * `fee_included` *bool* - set to True if amout + fee is the total desired
  out flow. Default to False.

<a name="dposlib.ark.Wallet.link"></a>
#### link

```python
 | link(*args, **kwargs)
```

See [`dposlib.ark.link`](ark.md#link).

<a name="dposlib.ark.Wallet.unlink"></a>
#### unlink

```python
 | unlink()
```

See [`dposlib.ark.unlink`](ark.md#unlink).

<a name="dposlib.ark.Wallet.send"></a>
#### send

```python
 | @isLinked
 | send(amount, address, vendorField=None, expiration=0)
```

Broadcast a transfer transaction to the ledger.
See [`dposlib.ark.v2.transfer`](v2.md#transfer).

<a name="dposlib.ark.Wallet.setSecondSecret"></a>
#### setSecondSecret

```python
 | @isLinked
 | setSecondSecret(secondSecret)
```

Broadcast a second secret registration transaction to the ledger.
See [`dposlib.ark.v2.registerSecondSecret`](
    v2.md#registersecondsecret
).

<a name="dposlib.ark.Wallet.setSecondPublicKey"></a>
#### setSecondPublicKey

```python
 | @isLinked
 | setSecondPublicKey(secondPublicKey)
```

Broadcast a second secret registration transaction into the ledger.
See [`dposlib.ark.v2.registerSecondPublicKey`](
    v2.md#registersecondpublickey
).

<a name="dposlib.ark.Wallet.setDelegate"></a>
#### setDelegate

```python
 | @isLinked
 | setDelegate(username)
```

Broadcast a delegate registration transaction to the ledger.
See [`dposlib.ark.v2.registerAsDelegate`](
    v2.md#registerasdelegate
).

<a name="dposlib.ark.Wallet.upVote"></a>
#### upVote

```python
 | @isLinked
 | upVote(*usernames)
```

Broadcast an up-vote transaction to the ledger.
See [`dposlib.ark.v2.upVote`](v2.md#upvote).

<a name="dposlib.ark.Wallet.downVote"></a>
#### downVote

```python
 | @isLinked
 | downVote(*usernames)
```

Broadcast a down-vote transaction to the ledger.
See [`dposlib.ark.v2.downVote`](v2.md#downvote).

<a name="dposlib.ark.crypto"></a>
# dposlib.ark.crypto

<a name="dposlib.ark.crypto.getKeys"></a>
#### getKeys

```python
getKeys(secret)
```

Generate keyring containing secp256k1 keys-pair and wallet import format
(WIF).

**Arguments**:

- `secret` _str, bytes or int_ - anything that could issue a private key on
  secp256k1 curve.
  

**Returns**:

- `dict` - public, private and WIF keys.

<a name="dposlib.ark.crypto.getMultiSignaturePublicKey"></a>
#### getMultiSignaturePublicKey

```python
getMultiSignaturePublicKey(minimum, *publicKeys)
```

Compute ARK multi signature public key according to [ARK AIP `18`](
https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-18.md
).

**Arguments**:

- `minimum` _int_ - minimum signature required.
- `publicKeys` _list of str_ - public key list.
  

**Returns**:

- `hex` - the multisignature public key.

<a name="dposlib.ark.crypto.getAddressFromSecret"></a>
#### getAddressFromSecret

```python
getAddressFromSecret(secret, marker=None)
```

Compute ARK address from secret.

**Arguments**:

- `secret` _str_ - secret string.
- `marker` _int_ - network marker (optional).
  

**Returns**:

- `base58` - the address.

<a name="dposlib.ark.crypto.getAddress"></a>
#### getAddress

```python
getAddress(publicKey, marker=None)
```

Compute ARK address from publicKey.

**Arguments**:

- `publicKey` _str_ - public key.
- `marker` _int_ - network marker (optional).
  

**Returns**:

- `base58` - the address.

<a name="dposlib.ark.crypto.getWIF"></a>
#### getWIF

```python
getWIF(seed)
```

Compute WIF address from seed.

**Arguments**:

- `seed` _bytes_ - a sha256 sequence bytes.
  

**Returns**:

- `base58` - the WIF address.

<a name="dposlib.ark.crypto.wifSignature"></a>
#### wifSignature

```python
wifSignature(tx, wif)
```

Generate transaction signature using private key.

**Arguments**:

- `tx` _dict or Transaction_ - transaction description.
- `wif` _str_ - wif key.
  

**Returns**:

- `hex` - signature.

<a name="dposlib.ark.crypto.wifSignatureFromBytes"></a>
#### wifSignatureFromBytes

```python
wifSignatureFromBytes(data, wif)
```

Generate signature from data using WIF key.

**Arguments**:

- `data` _bytes_ - bytes sequence.
- `wif` _str_ - wif key.
  

**Returns**:

- `hex` - signature.

<a name="dposlib.ark.crypto.getSignature"></a>
#### getSignature

```python
getSignature(tx, privateKey, **options)
```

Generate transaction signature using private key.

**Arguments**:

- `tx` _dict or Transaction_ - transaction description.
- `privateKey` _str_ - private key as hex string.
  
  **Options**:
  
  * `exclude_sig` *bool* - exclude signature during tx serialization.
  Defalut to True.
  * `exclude_multi_sig` *bool* - exclude signatures during tx
  serialization. Defalut to True.
  * `exclude_second_sig` *bool* - exclude second signatures during tx
  serialization. Defalut to True.
  

**Returns**:

- `hex` - signature.

<a name="dposlib.ark.crypto.getSignatureFromBytes"></a>
#### getSignatureFromBytes

```python
getSignatureFromBytes(data, privateKey)
```

Generate signature from data using private key.

**Arguments**:

- `data` _bytes_ - bytes sequence.
- `privateKey` _str_ - private key as hex string.
  

**Returns**:

- `hex` - signature.

<a name="dposlib.ark.crypto.verifySignature"></a>
#### verifySignature

```python
verifySignature(value, publicKey, signature)
```

Verify signature.

**Arguments**:

- `value` _str_ - value as hex string.
- `publicKey` _str_ - public key as hex string.
- `signature` _str_ - signature as hex string.
  

**Returns**:

- `bool` - True if signature matches the public key.

<a name="dposlib.ark.crypto.verifySignatureFromBytes"></a>
#### verifySignatureFromBytes

```python
verifySignatureFromBytes(data, publicKey, signature)
```

Verify signature.

**Arguments**:

- `data` _bytes_ - data.
- `publicKey` _str_ - public key as hex string.
- `signature` _str_ - signature as hex string.
  

**Returns**:

- `bool` - True if signature matches the public key.

<a name="dposlib.ark.crypto.getId"></a>
#### getId

```python
getId(tx)
```

Generate transaction id.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
  

**Returns**:

- `hex` - id.

<a name="dposlib.ark.crypto.getIdFromBytes"></a>
#### getIdFromBytes

```python
getIdFromBytes(data)
```

Generate data id.

**Arguments**:

- `data` _bytes_ - data as bytes sequence.
  

**Returns**:

- `hex` - id.

<a name="dposlib.ark.crypto.getBytes"></a>
#### getBytes

```python
getBytes(tx, **options)
```

Hash transaction.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
  
  **Options**:
  
  * `exclude_sig` *bool* - exclude signature during tx serialization.
  Defalut to True.
  * `exclude_multi_sig` *bool* - exclude signatures during tx
  serialization. Defalut to True.
  * `exclude_second_sig` *bool* - exclude second signatures during tx
  serialization. Defalut to True.
  

**Returns**:

- `bytes` - transaction serial.

<a name="dposlib.ark.crypto.checkTransaction"></a>
#### checkTransaction

```python
checkTransaction(tx, secondPublicKey=None, multiPublicKeys=[])
```

Verify transaction validity.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
- `secondPublicKey` _str_ - second public key to use if needed.
- `multiPublicKeys` _list_ - owners public keys (sorted according to
  associated type-4-tx asset).
  

**Returns**:

- `bool` - True if transaction is valid.

<a name="dposlib.ark.tx"></a>
# dposlib.ark.tx

<a name="dposlib.ark.tx.Transaction"></a>
## Transaction Objects

```python
class Transaction(dict)
```

A python `dict` that implements all the necessities to manually generate
valid transactions.

<a name="dposlib.ark.tx.Transaction.feeIncluded"></a>
#### feeIncluded

If `True` then `amount` + `fee` = total arktoshi flow

<a name="dposlib.ark.tx.Transaction.useDynamicFee"></a>
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

- `value` _str or int_ - constant or fee multiplier.

<a name="dposlib.ark.tx.Transaction.link"></a>
#### link

```python
 | link(secret=None, secondSecret=None)
```

Save public and private keys derived from secrets. This is equivalent
to wallet login. it limits number of secret keyboard entries.

**Arguments**:

- `secret` _str_ - passphrase.
- `secondSecret` _str_ - second passphrase.

<a name="dposlib.ark.tx.Transaction.sign"></a>
#### sign

```python
 | sign()
```

Generate the `signature` field. Private key have to be set first.

<a name="dposlib.ark.tx.Transaction.signSign"></a>
#### signSign

```python
 | signSign()
```

Generate the `signSignature` field. Transaction have to be signed and
second  private key have to be set first.

<a name="dposlib.ark.tx.Transaction.signWithSecret"></a>
#### signWithSecret

```python
 | signWithSecret(secret)
```

Generate the `signature` field using passphrase. The associated
public and private keys are stored till [`dposlib.ark.unlink`](
ark.md#unlink
) is called.

**Arguments**:

- `secret` _`str`_ - passphrase.

<a name="dposlib.ark.tx.Transaction.signSignWithSecondSecret"></a>
#### signSignWithSecondSecret

```python
 | signSignWithSecondSecret(secondSecret)
```

Generate the `signSignature` field using second passphrase. The
associated second public and private keys are stored till
[`dposlib.ark.unlink`](ark.md#unlink) is called.

**Arguments**:

- `secondSecret` _`str`_ - second passphrase.

<a name="dposlib.ark.tx.Transaction.multiSignWithSecret"></a>
#### multiSignWithSecret

```python
 | multiSignWithSecret(secret)
```

Add a signature in `signatures` field.

**Arguments**:

- `index` _int_ - signature index.
- `secret` _str_ - passphrase.

<a name="dposlib.ark.tx.Transaction.signWithKeys"></a>
#### signWithKeys

```python
 | signWithKeys(publicKey, privateKey)
```

Generate the `signature` field using public and private keys. They
are stored till [`dposlib.ark.unlink`](ark.md#unlink) is called.

**Arguments**:

- `publicKey` _str_ - public key as hex string.
- `privateKey` _str_ - private key as hex string.

<a name="dposlib.ark.tx.Transaction.signSignWithKey"></a>
#### signSignWithKey

```python
 | signSignWithKey(secondPrivateKey)
```

Generate the `signSignature` field using second private key. It is
stored till [`dposlib.ark.unlink`](ark.md#unlink) is called.

**Arguments**:

- `secondPrivateKey` _`str`_ - second private key as hex string.

<a name="dposlib.ark.tx.Transaction.multiSignWithKey"></a>
#### multiSignWithKey

```python
 | multiSignWithKey(privateKey)
```

Add a signature in `signatures` field according to given index and
privateKey.

**Arguments**:

- `privateKey` _str_ - private key as hex string.

<a name="dposlib.ark.tx.Transaction.identify"></a>
#### identify

```python
 | identify()
```

Generate the `id` field. Transaction have to be signed.

<a name="dposlib.ark.tx.Transaction.finalize"></a>
#### finalize

```python
 | finalize(secret=None, secondSecret=None, fee=None, fee_included=False)
```

Finalize a transaction by setting `fee`, signatures and `id`.

**Arguments**:

- `secret` _str_ - passphrase.
- `secondSecret` _str_ - second passphrase.
- `fee` _int_ - manually set fee value in `arktoshi`.
- `fee_included` _bool_ - see
  [`dposlib.ark.tx.Transaction.feeIncluded`](ark.md#feeincluded).

