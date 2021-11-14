<a name="dposlib.ark.api"></a>
# dposlib.ark.api

<a name="dposlib.ark.api.isLinked"></a>
#### isLinked

```python
isLinked(func)
```

`Python decorator`.
First argument of decorated function have to be a
[`dposlib.ark.api.Content`](ark.md#dposlib.ark.api.Content)
or an object containing a valid `address`, `_derivationPath` or `publicKey`
attribute. It executes the decorated `function` if the object is correctly
linked using `dposlib.ark.api.link` definition.

<a name="dposlib.ark.api.link"></a>
#### link

```python
link(cls, secret=None, secondSecret=None)
```

Associates crypto keys into a [`dposlib.ark.api.Content`](
ark.md#dposlib.ark.api.Content
) object according to secrets. If `secret` or `secondSecret` are not `str`,
they are considered as `None`. In this case secrets will be asked and
checked from console untill success or `Ctrl+c` keyboard interruption.

**Arguments**:

- `cls` _Content_ - content object.
- `secret` _str_ - secret string. Default set to `None`.
- `secondSecret` _str_ - second secret string. Default set to `None`.
  

**Returns**:

- `bool` - True if secret and second secret match.

<a name="dposlib.ark.api.unlink"></a>
#### unlink

```python
unlink(cls)
```

Remove crypto keys association.

<a name="dposlib.ark.api.JSDict"></a>
## JSDict Objects

```python
class JSDict(dict)
```

Read only dictionary with js object behaviour.

```python
>>> jsdic = dposlib.ark.JSDict(value=5)
>>> jsdic
{'value': 5}
>>> jsdic.value
5
```

<a name="dposlib.ark.api.Content"></a>
## Content Objects

```python
class Content(object)
```

Live object connected to blockchain. It is initialized with
[`dposlib.rest.GET`](rest.md#dposlib.rest.GET) request. Object is updated
every 30s. Endpoint response can be a `dict` or a `list`. If it is a
`list`, it is stored in `data` attribute else all fields are stored as
instance attribute.

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

<a name="dposlib.ark.api.Content.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(ndpt, *args, **kwargs)
```

**Arguments**:

- `ndpt` _usrv.req.Endpoint_ - endpoint class to be called.
- `*args` - Variable length argument list used by `usrv.req.Endpoint`.
  
  **Kwargs**:
  
  * `keep_alive` *bool* - set hook to update data from blockcahin.
  Default to True.

<a name="dposlib.ark.api.Content.filter"></a>
#### filter

```python
 | filter(data)
```

Convert data as JSDict object converting string values in int if
possible.

<a name="dposlib.ark.api.Wallet"></a>
## Wallet Objects

```python
class Wallet(Content)
```

Wallet root class that implements basic wallet behaviour.

<a name="dposlib.ark.api.Wallet.delegate"></a>
#### delegate

Delegate attributes if wallet is registered as delegate.

<a name="dposlib.ark.api.Wallet.username"></a>
#### username

Delegate username if wallet is registered as delegate.

<a name="dposlib.ark.api.Wallet.secondPublicKey"></a>
#### secondPublicKey

Second public key if second signature is set to wallet.

<a name="dposlib.ark.api.Wallet.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(address, **kw)
```

**Arguments**:

- `address` _str_ - wallet address or delegate username.
- `**kwargs` - Variable key argument used by
  [`dposlib.ark.api.Content`](ark.md#dposlib.ark.api.Content).
  
  **Specific kwargs**:
  
  * `keep_alive` *bool* - automatic update data from blockcahin. Default
  to True.
  * `fee` *int or str* - set fee level as fee multiplier string value or
  one of **minFee**, **avgFee**, **maxFee**. Default to **avgFee**.
  * `fee_included` *bool* - set to True if amout + fee is the total
  desired out flow. Default to False.

<a name="dposlib.ark.api.Wallet.link"></a>
#### link

```python
 | link(*args, **kwargs)
```

See [`dposlib.ark.api.link`](ark.md#dposlib.ark.api.link).

<a name="dposlib.ark.api.Wallet.unlink"></a>
#### unlink

```python
 | unlink()
```

See [`dposlib.ark.api.unlink`](ark.md#dposlib.ark.api.unlink).

<a name="dposlib.ark.api.Wallet.send"></a>
#### send

```python
 | @isLinked
 | send(amount, address, vendorField=None, expiration=0)
```

Broadcast a transfer transaction to the ledger.
See [`dposlib.ark.builders.transfer`](
    ark.md#dposlib.ark.builders.transfer
).

<a name="dposlib.ark.api.Wallet.setSecondSecret"></a>
#### setSecondSecret

```python
 | @isLinked
 | setSecondSecret(secondSecret)
```

Broadcast a second secret registration transaction to the ledger.
See [`dposlib.ark.builders.registerSecondSecret`](
    ark.md#dposlib.ark.builders.registerSecondSecret
).

<a name="dposlib.ark.api.Wallet.setSecondPublicKey"></a>
#### setSecondPublicKey

```python
 | @isLinked
 | setSecondPublicKey(secondPublicKey)
```

Broadcast a second secret registration transaction into the ledger.
See [`dposlib.ark.builders.registerSecondPublicKey`](
   ark.md#dposlib.ark.builders.registerSecondPublicKey
).

<a name="dposlib.ark.api.Wallet.setDelegate"></a>
#### setDelegate

```python
 | @isLinked
 | setDelegate(username)
```

Broadcast a delegate registration transaction to the ledger.
See [`dposlib.ark.builders.registerAsDelegate`](
    ark.md#dposlib.ark.builders.registerAsDelegate
).

<a name="dposlib.ark.api.Wallet.upVote"></a>
#### upVote

```python
 | @isLinked
 | upVote(*usernames)
```

Broadcast an up-vote transaction to the ledger.
See [`dposlib.ark.builders.multiVote`](
    ark.md#dposlib.ark.builders.multiVote
).

<a name="dposlib.ark.api.Wallet.downVote"></a>
#### downVote

```python
 | @isLinked
 | downVote(*usernames)
```

Broadcast a down-vote transaction to the ledger.
See [`dposlib.ark.builders.downVote`](
    ark.md#dposlib.ark.builders.downVote
).

<a name="dposlib.ark.api.Wallet.sendIpfs"></a>
#### sendIpfs

```python
 | @isLinked
 | sendIpfs(ipfs)
```

See [`dposlib.ark.builders.registerIpfs`](
    ark.md#dposlib.ark.builders.registerIpfs
).

<a name="dposlib.ark.api.Wallet.multiSend"></a>
#### multiSend

```python
 | @isLinked
 | multiSend(*pairs, **kwargs)
```

See [`dposlib.ark.builder.multiPayment`](
    ark.md#dposlib.ark.builders.multiPayment
).

<a name="dposlib.ark.api.Wallet.resignate"></a>
#### resignate

```python
 | @isLinked
 | resignate()
```

See [`dposlib.ark.builders.delegateResignation`](
    ark.md#dposlib.ark.builders.delegateResignation
).

<a name="dposlib.ark.api.Wallet.sendHtlc"></a>
#### sendHtlc

```python
 | @isLinked
 | sendHtlc(amount, address, secret, expiration=24, vendorField=None)
```

See [`dposlib.ark.builders.htlcLock`](
    ark.md#dposlib.ark.builders.htlcLock
).

<a name="dposlib.ark.api.Wallet.claimHtlc"></a>
#### claimHtlc

```python
 | @isLinked
 | claimHtlc(txid, secret)
```

See [`dposlib.ark.builders.htlcClaim`](
    ark.md#dposlib.ark.builders.htlcClaim
).

<a name="dposlib.ark.api.Wallet.refundHtlc"></a>
#### refundHtlc

```python
 | @isLinked
 | refundHtlc(txid)
```

See [`dposlib.ark.builders.htlcRefund`](
    ark.md#dposlib.ark.builders.htlcRefund
).

<a name="dposlib.ark.api.Wallet.createEntity"></a>
#### createEntity

```python
 | @isLinked
 | createEntity(name, type="business", subtype=0, ipfsData=None)
```

See [`dposlib.ark.builders.entityRegister`](
    ark.md#dposlib.ark.builders.entityRegister
).

<a name="dposlib.ark.api.Wallet.updateEntity"></a>
#### updateEntity

```python
 | @isLinked
 | updateEntity(registrationId, ipfsData, name=None)
```

See [`dposlib.ark.builders.entityUpdate`](
    ark.md#dposlib.ark.builders.entityUpdate
).

<a name="dposlib.ark.api.Wallet.resignEntity"></a>
#### resignEntity

```python
 | @isLinked
 | resignEntity(registrationId)
```

See [`dposlib.ark.builders.entityResign`](
    ark.md#dposlib.ark.builders.entityResign
).

<a name="dposlib.ark.builders"></a>
# dposlib.ark.builders

<a name="dposlib.ark.builders.transfer"></a>
#### transfer

```python
transfer(amount, address, vendorField=None, expiration=0)
```

Build a transfer transaction. Emoji can be included in transaction
vendorField using unicode formating.


```python
>>> vendorField = u"message with sparkles \u2728"
```

**Arguments**:

- `amount` _float_ - transaction amount in ark.
- `address` _str_ - valid recipient address.
- `vendorField` _str_ - vendor field message.
- `expiration` _float_ - time of persistance in hour.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.registerSecondSecret"></a>
#### registerSecondSecret

```python
registerSecondSecret(secondSecret)
```

Build a second secret registration transaction.

**Arguments**:

- `secondSecret` _str_ - passphrase.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.registerSecondPublicKey"></a>
#### registerSecondPublicKey

```python
registerSecondPublicKey(secondPublicKey)
```

Build a second secret registration transaction.

*You must own the secret issuing secondPublicKey*

**Arguments**:

- `secondPublicKey` _str_ - public key as hex string.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.registerAsDelegate"></a>
#### registerAsDelegate

```python
registerAsDelegate(username)
```

Build a delegate registration transaction.

**Arguments**:

- `username` _str_ - delegate username.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.upVote"></a>
#### upVote

```python
upVote(*usernames)
```

Build an upvote transaction.

**Arguments**:

- `usernames` _iterable_ - delegate usernames as str iterable.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.downVote"></a>
#### downVote

```python
downVote(*usernames)
```

Build a downvote transaction.

**Arguments**:

- `usernames` _iterable_ - delegate usernames as str iterable.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.registerMultiSignature"></a>
#### registerMultiSignature

```python
registerMultiSignature(minSig, *publicKeys)
```

Build a multisignature registration transaction.

**Arguments**:

- `minSig` _int_ - minimum signature required.
- `publicKeys` _list of str_ - public key list.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.registerIpfs"></a>
#### registerIpfs

```python
registerIpfs(ipfs)
```

Build an IPFS registration transaction.

**Arguments**:

- `ipfs` _str_ - ipfs DAG.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.multiPayment"></a>
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

- `pairs` _iterable_ - recipient-amount pair iterable.
- `vendorField` _str_ - vendor field message.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.delegateResignation"></a>
#### delegateResignation

```python
delegateResignation()
```

Build a delegate resignation transaction.

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.htlcSecret"></a>
#### htlcSecret

```python
htlcSecret(secret)
```

Compute an HTLC secret hex string from passphrase.

**Arguments**:

- `secret` _str_ - passphrase.
  

**Returns**:

  hex str: HTLC secret.

<a name="dposlib.ark.builders.htlcLock"></a>
#### htlcLock

```python
htlcLock(amount, address, secret, expiration=24, vendorField=None)
```

Build an HTLC lock transaction. Emoji can be included in transaction
vendorField using unicode formating.


```python
>>> vendorField = u"message with sparkles \u2728"
```

**Arguments**:

- `amount` _float_ - transaction amount in ark.
- `address` _str_ - valid recipient address.
- `secret` _str_ - lock passphrase.
- `expiration` _float_ - transaction validity in hour.
- `vendorField` _str_ - vendor field message.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.htlcClaim"></a>
#### htlcClaim

```python
htlcClaim(txid, secret)
```

Build an HTLC claim transaction.

**Arguments**:

- `txid` _str_ - htlc lock transaction id.
- `secret` _str_ - passphrase used by htlc lock transaction.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.htlcRefund"></a>
#### htlcRefund

```python
htlcRefund(txid)
```

Build an HTLC refund transaction.

**Arguments**:

- `txid` _str_ - htlc lock transaction id.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.entityRegister"></a>
#### entityRegister

```python
entityRegister(name, type="business", subtype=0, ipfsData=None)
```

Build an entity registration.

**Arguments**:

- `name` _str_ - entity name
- `type` _str_ - entity type. Possible values are `business`, `product`,
  `plugin`, `module` and `delegate`. Default to `business`.
- `subtype` _int_ - entity subtype
- `ipfsData` _base58_ - ipfs DAG. Default to None.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.entityUpdate"></a>
#### entityUpdate

```python
entityUpdate(registrationId, ipfsData, name=None)
```

Build an entity update.

**Arguments**:

- `registrationId` _str_ - registration id
- `ipfsData` _base58_ - ipfs DAG. Default to None.
- `name` _str, optional_ - entity name
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.entityResign"></a>
#### entityResign

```python
entityResign(registrationId)
```

Build an entity resignation.

**Arguments**:

- `registrationId` _str_ - registration id
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a name="dposlib.ark.builders.multiVote"></a>
#### multiVote

```python
multiVote(tx)
```

Transform a [`dposlib.ark.builders.upVote`](
ark.md#dposlib.ark.builders.upVote
) transaction into a multivote one. It makes the transaction downvote
former delegate if any and then apply new vote.

**Arguments**:

- `tx` _dposlib.ark.tx.Transaction_ - upVote transaction.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

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

<a name="dposlib.ark.tx.serialize"></a>
#### serialize

```python
serialize(tx, **options)
```

Serialize transaction.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
  

**Returns**:

- `bytes` - transaction serial representation.

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
second private key have to be set first.

<a name="dposlib.ark.tx.Transaction.signWithSecret"></a>
#### signWithSecret

```python
 | signWithSecret(secret)
```

Generate the `signature` field using passphrase. The associated
public and private keys are stored till `dposlib.ark.unlink` is called.

**Arguments**:

- `secret` _`str`_ - passphrase.

<a name="dposlib.ark.tx.Transaction.signSignWithSecondSecret"></a>
#### signSignWithSecondSecret

```python
 | signSignWithSecondSecret(secondSecret)
```

Generate the `signSignature` field using second passphrase. The
associated second public and private keys are stored till
`dposlib.ark.unlink` is called.

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
are stored till `dposlib.ark.unlink` is called.

**Arguments**:

- `publicKey` _str_ - public key as hex string.
- `privateKey` _str_ - private key as hex string.

<a name="dposlib.ark.tx.Transaction.signSignWithKey"></a>
#### signSignWithKey

```python
 | signSignWithKey(secondPrivateKey)
```

Generate the `signSignature` field using second private key. It is
stored till `dposlib.ark.unlink` is called.

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
- `fee_included` _bool_ - see `dposlib.ark.tx.Transaction.feeIncluded`.

