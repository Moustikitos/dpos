<a id="dposlib.ark.tx"></a>

# dposlib.ark.tx

<a id="dposlib.ark.tx.serialize"></a>

#### serialize

```python
def serialize(tx, **options)
```

Serialize transaction.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
  

**Returns**:

- `bytes` - transaction serial representation.

<a id="dposlib.ark.tx.Transaction"></a>

## Transaction Objects

```python
class Transaction(dict)
```

A python `dict` that implements all the necessities to manually generate
valid transactions.

<a id="dposlib.ark.tx.Transaction.feeIncluded"></a>

#### feeIncluded

If `True` then `amount` + `fee` = total arktoshi flow

<a id="dposlib.ark.tx.Transaction.useDynamicFee"></a>

#### useDynamicFee

```python
@staticmethod
def useDynamicFee(value="minFee")
```

Activate and configure dynamic fees parameters. Value can be either an
integer defining the fee multiplier constant or a string defining the
fee level to use acccording to the 30-days-average. possible values are
`avgFee` `minFee` (default) and `maxFee`.

**Arguments**:

- `value` _str or int_ - constant or fee multiplier.

<a id="dposlib.ark.tx.Transaction.link"></a>

#### link

```python
def link(secret=None, secondSecret=None)
```

Save public and private keys derived from secrets. This is equivalent
to wallet login. it limits number of secret keyboard entries.

**Arguments**:

- `secret` _str_ - passphrase.
- `secondSecret` _str_ - second passphrase.

<a id="dposlib.ark.tx.Transaction.unlink"></a>

#### unlink

```python
def unlink()
```

Remove all ownership parameters. The transaction return to orphan mode.

<a id="dposlib.ark.tx.Transaction.touch"></a>

#### touch

```python
def touch()
```

Update inner parameters using blockchain connection.

<a id="dposlib.ark.tx.Transaction.sign"></a>

#### sign

```python
def sign()
```

Generate the `signature` field. Private key have to be set first.

<a id="dposlib.ark.tx.Transaction.signSign"></a>

#### signSign

```python
def signSign()
```

Generate the `signSignature` field. Transaction have to be signed and
second private key have to be set first.

<a id="dposlib.ark.tx.Transaction.signWithSecret"></a>

#### signWithSecret

```python
def signWithSecret(secret)
```

Generate the `signature` field using passphrase. The associated
public and private keys are stored till `dposlib.ark.unlink` is called.

**Arguments**:

- `secret` _`str`_ - passphrase.

<a id="dposlib.ark.tx.Transaction.signSignWithSecondSecret"></a>

#### signSignWithSecondSecret

```python
def signSignWithSecondSecret(secondSecret)
```

Generate the `signSignature` field using second passphrase. The
associated second public and private keys are stored till
`dposlib.ark.unlink` is called.

**Arguments**:

- `secondSecret` _`str`_ - second passphrase.

<a id="dposlib.ark.tx.Transaction.multiSignWithSecret"></a>

#### multiSignWithSecret

```python
def multiSignWithSecret(secret)
```

Add a signature in `signatures` field.

**Arguments**:

- `index` _int_ - signature index.
- `secret` _str_ - passphrase.

<a id="dposlib.ark.tx.Transaction.signWithKeys"></a>

#### signWithKeys

```python
def signWithKeys(publicKey, privateKey)
```

Generate the `signature` field using public and private keys. They
are stored till `dposlib.ark.unlink` is called.

**Arguments**:

- `publicKey` _str_ - public key as hex string.
- `privateKey` _str_ - private key as hex string.

<a id="dposlib.ark.tx.Transaction.signSignWithKey"></a>

#### signSignWithKey

```python
def signSignWithKey(secondPrivateKey)
```

Generate the `signSignature` field using second private key. It is
stored till `dposlib.ark.unlink` is called.

**Arguments**:

- `secondPrivateKey` _`str`_ - second private key as hex string.

<a id="dposlib.ark.tx.Transaction.multiSignWithKey"></a>

#### multiSignWithKey

```python
def multiSignWithKey(privateKey)
```

Add a signature in `signatures` field according to given index and
privateKey.

**Arguments**:

- `privateKey` _str_ - private key as hex string.

<a id="dposlib.ark.tx.Transaction.appendMultiSignature"></a>

#### appendMultiSignature

```python
def appendMultiSignature(publicKey, signature)
```

Manage the place of signature in signatures list for multisignature
wallet transaction or registration.

<a id="dposlib.ark.tx.Transaction.identify"></a>

#### identify

```python
def identify()
```

Generate the `id` field. Transaction have to be signed.

<a id="dposlib.ark.tx.Transaction.finalize"></a>

#### finalize

```python
def finalize(secret=None, secondSecret=None, fee=None, fee_included=False)
```

Finalize a transaction by setting `fee`, signatures and `id`.

**Arguments**:

- `secret` _str_ - passphrase.
- `secondSecret` _str_ - second passphrase.
- `fee` _int_ - manually set fee value in `arktoshi`.
- `fee_included` _bool_ - see `dposlib.ark.tx.Transaction.feeIncluded`.

