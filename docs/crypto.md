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
  secp256k1 curve

**Returns**:

  public, private and WIF keys

<a name="dposlib.ark.crypto.getMultiSignaturePublicKey"></a>
#### getMultiSignaturePublicKey

```python
getMultiSignaturePublicKey(minimum, *publicKeys)
```

Compute ARK multi signature public key according to [ARK AIP `18`](
https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-18.md
).

**Arguments**:

- `minimum` _int_ - minimum signature required
- `publicKeys` _list of str_ - public key list

**Returns**:

  the multisignature public key

<a name="dposlib.ark.crypto.getAddressFromSecret"></a>
#### getAddressFromSecret

```python
getAddressFromSecret(secret, marker=None)
```

Compute ARK address from secret.

**Arguments**:

- `secret` _str_ - secret string
- `marker` _int_ - network marker (optional)

**Returns**:

  the address

<a name="dposlib.ark.crypto.getAddress"></a>
#### getAddress

```python
getAddress(publicKey, marker=None)
```

Compute ARK address from publicKey.

**Arguments**:

- `publicKey` _str_ - public key
- `marker` _int_ - network marker (optional)

**Returns**:

  the address

<a name="dposlib.ark.crypto.getWIF"></a>
#### getWIF

```python
getWIF(seed)
```

Compute WIF address from seed.

**Arguments**:

- `seed` _bytes_ - a sha256 sequence bytes

**Returns**:

  WIF address

<a name="dposlib.ark.crypto.wifSignature"></a>
#### wifSignature

```python
wifSignature(tx, wif)
```

Generate transaction signature using private key.

**Arguments**:

- `tx` _dict or Transaction_ - transaction description
- `wif` _str_ - wif key

**Returns**:

  signature

<a name="dposlib.ark.crypto.wifSignatureFromBytes"></a>
#### wifSignatureFromBytes

```python
wifSignatureFromBytes(data, wif)
```

Generate signature from data using WIF key.

**Arguments**:

- `data` _bytes_ - bytes sequence
- `wif` _str_ - wif key

**Returns**:

  signature

<a name="dposlib.ark.crypto.getSignature"></a>
#### getSignature

```python
getSignature(tx, privateKey, **options)
```

Generate transaction signature using private key.

**Arguments**:

- `tx` _dict or Transaction_ - transaction description
- `privateKey` _str_ - private key as hex string
  Keyword args:
  exclude_sig (bool):
  exclude signature during tx serialization [defalut: True]
  exclude_multi_sig(bool):
  exclude signatures during tx serialization [defalut: True]
  exclude_second_sig(bool):
  exclude second signatures during tx serialization [defalut: True]

**Returns**:

  signature

<a name="dposlib.ark.crypto.getSignatureFromBytes"></a>
#### getSignatureFromBytes

```python
getSignatureFromBytes(data, privateKey)
```

Generate signature from data using private key.

**Arguments**:

- `data` _bytes_ - bytes sequence
- `privateKey` _str_ - private key as hex string

**Returns**:

  signature as hex string

<a name="dposlib.ark.crypto.verifySignature"></a>
#### verifySignature

```python
verifySignature(value, publicKey, signature)
```

Verify signature.

**Arguments**:

- `value` _str_ - value as hex string
- `publicKey` _str_ - public key as hex string
- `signature` _str_ - signature as hex string

**Returns**:

  True if signature matches the public key

<a name="dposlib.ark.crypto.verifySignatureFromBytes"></a>
#### verifySignatureFromBytes

```python
verifySignatureFromBytes(data, publicKey, signature)
```

Verify signature.

**Arguments**:

- `data` _bytes_ - data
- `publicKey` _str_ - public key as hex string
- `signature` _str_ - signature as hex string

**Returns**:

  True if signature matches the public key

<a name="dposlib.ark.crypto.getId"></a>
#### getId

```python
getId(tx)
```

Generate transaction id.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object

**Returns**:

  id as hex string

<a name="dposlib.ark.crypto.getIdFromBytes"></a>
#### getIdFromBytes

```python
getIdFromBytes(data)
```

Generate data id.

**Arguments**:

- `data` _bytes_ - data as bytes sequence

**Returns**:

  id as hex string

<a name="dposlib.ark.crypto.getBytes"></a>
#### getBytes

```python
getBytes(tx, **options)
```

Hash transaction.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object
  Keyword args:
  exclude_sig (bool):
  exclude signature during tx serialization [defalut: True]
  exclude_multi_sig(bool):
  exclude signatures during tx serialization [defalut: True]
  exclude_second_sig(bool):
  exclude second signatures during tx serialization [defalut: True]

**Returns**:

  bytes sequence

<a name="dposlib.ark.crypto.checkTransaction"></a>
#### checkTransaction

```python
checkTransaction(tx, secondPublicKey=None, multiPublicKeys=[])
```

Verify transaction validity.

**Arguments**:

  tx (dict or Transaction):
  transaction object
  secondPublicKey (str):
  second public key to use if needed
  multiPublicKeys (list):
  owners public keys (sorted according to associated type-4-tx asset)

**Returns**:

  True if transaction is valid

