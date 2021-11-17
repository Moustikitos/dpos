<a id="dposlib.ark.builders"></a>

# dposlib.ark.builders

<a id="dposlib.ark.builders.transfer"></a>

#### transfer

```python
def transfer(amount, address, vendorField=None, expiration=0)
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

<a id="dposlib.ark.builders.registerSecondSecret"></a>

#### registerSecondSecret

```python
def registerSecondSecret(secondSecret)
```

Build a second secret registration transaction.

**Arguments**:

- `secondSecret` _str_ - passphrase.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.registerSecondPublicKey"></a>

#### registerSecondPublicKey

```python
def registerSecondPublicKey(secondPublicKey)
```

Build a second secret registration transaction.

*You must own the secret issuing secondPublicKey*

**Arguments**:

- `secondPublicKey` _str_ - public key as hex string.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.registerAsDelegate"></a>

#### registerAsDelegate

```python
def registerAsDelegate(username)
```

Build a delegate registration transaction.

**Arguments**:

- `username` _str_ - delegate username.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.upVote"></a>

#### upVote

```python
def upVote(*usernames)
```

Build an upvote transaction.

**Arguments**:

- `usernames` _iterable_ - delegate usernames as str iterable.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.downVote"></a>

#### downVote

```python
def downVote(*usernames)
```

Build a downvote transaction.

**Arguments**:

- `usernames` _iterable_ - delegate usernames as str iterable.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.registerMultiSignature"></a>

#### registerMultiSignature

```python
def registerMultiSignature(minSig, *publicKeys)
```

Build a multisignature registration transaction.

**Arguments**:

- `minSig` _int_ - minimum signature required.
- `publicKeys` _list of str_ - public key list.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.registerIpfs"></a>

#### registerIpfs

```python
def registerIpfs(ipfs)
```

Build an IPFS registration transaction.

**Arguments**:

- `ipfs` _str_ - ipfs DAG.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.multiPayment"></a>

#### multiPayment

```python
def multiPayment(*pairs, **kwargs)
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

<a id="dposlib.ark.builders.delegateResignation"></a>

#### delegateResignation

```python
def delegateResignation()
```

Build a delegate resignation transaction.

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.htlcSecret"></a>

#### htlcSecret

```python
def htlcSecret(secret)
```

Compute an HTLC secret hex string from passphrase.

**Arguments**:

- `secret` _str_ - passphrase.
  

**Returns**:

  hex str: HTLC secret.

<a id="dposlib.ark.builders.htlcLock"></a>

#### htlcLock

```python
def htlcLock(amount, address, secret, expiration=24, vendorField=None)
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

<a id="dposlib.ark.builders.htlcClaim"></a>

#### htlcClaim

```python
def htlcClaim(txid, secret)
```

Build an HTLC claim transaction.

**Arguments**:

- `txid` _str_ - htlc lock transaction id.
- `secret` _str_ - passphrase used by htlc lock transaction.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.htlcRefund"></a>

#### htlcRefund

```python
def htlcRefund(txid)
```

Build an HTLC refund transaction.

**Arguments**:

- `txid` _str_ - htlc lock transaction id.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.entityRegister"></a>

#### entityRegister

```python
def entityRegister(name, type="business", subtype=0, ipfsData=None)
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

<a id="dposlib.ark.builders.entityUpdate"></a>

#### entityUpdate

```python
def entityUpdate(registrationId, ipfsData, name=None)
```

Build an entity update.

**Arguments**:

- `registrationId` _str_ - registration id
- `ipfsData` _base58_ - ipfs DAG. Default to None.
- `name` _str, optional_ - entity name
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.entityResign"></a>

#### entityResign

```python
def entityResign(registrationId)
```

Build an entity resignation.

**Arguments**:

- `registrationId` _str_ - registration id
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.ark.builders.multiVote"></a>

#### multiVote

```python
def multiVote(tx)
```

Transform a [`dposlib.ark.builders.upVote`](
builders.md#dposlib.ark.builders.upVote
) transaction into a multivote one. It makes the transaction downvote
former delegate if any and then apply new vote.

**Arguments**:

- `tx` _dposlib.ark.tx.Transaction_ - upVote transaction.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

