<a id="dposlib.ark.crypto"></a>

# dposlib.ark.crypto

<a id="dposlib.ark.crypto.getKeys"></a>

#### getKeys

```python
def getKeys(secret)
```

Generate keyring containing secp256k1 keys-pair and wallet import format
(WIF).

**Arguments**:

- `secret` _str, bytes or int_ - anything that could issue a private key on
  secp256k1 curve.
  

**Returns**:

- `dict` - public, private and WIF keys.

<a id="dposlib.ark.crypto.getMultiSignaturePublicKey"></a>

#### getMultiSignaturePublicKey

```python
def getMultiSignaturePublicKey(minimum, *publicKeys)
```

Compute ARK multi signature public key according to [ARK AIP `18`](
https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-18.md
).

**Arguments**:

- `minimum` _int_ - minimum signature required.
- `publicKeys` _list of str_ - public key list.
  

**Returns**:

- `hex` - the multisignature public key.

<a id="dposlib.ark.crypto.getAddressFromSecret"></a>

#### getAddressFromSecret

```python
def getAddressFromSecret(secret, marker=None)
```

Compute ARK address from secret.

**Arguments**:

- `secret` _str_ - secret string.
- `marker` _int_ - network marker (optional).
  

**Returns**:

- `base58` - the address.

<a id="dposlib.ark.crypto.getAddress"></a>

#### getAddress

```python
def getAddress(publicKey, marker=None)
```

Compute ARK address from publicKey.

**Arguments**:

- `publicKey` _str_ - public key.
- `marker` _int_ - network marker (optional).
  

**Returns**:

- `base58` - the address.

<a id="dposlib.ark.crypto.getWIF"></a>

#### getWIF

```python
def getWIF(seed)
```

Compute WIF address from seed.

**Arguments**:

- `seed` _bytes_ - a sha256 sequence bytes.
  

**Returns**:

- `base58` - the WIF address.

<a id="dposlib.ark.crypto.wifSignature"></a>

#### wifSignature

```python
def wifSignature(tx, wif)
```

Generate transaction signature using private key.

**Arguments**:

- `tx` _dict or Transaction_ - transaction description.
- `wif` _str_ - wif key.
  

**Returns**:

- `hex` - signature.

<a id="dposlib.ark.crypto.wifSignatureFromBytes"></a>

#### wifSignatureFromBytes

```python
def wifSignatureFromBytes(data, wif)
```

Generate signature from data using WIF key.

**Arguments**:

- `data` _bytes_ - bytes sequence.
- `wif` _str_ - wif key.
  

**Returns**:

- `hex` - signature.

<a id="dposlib.ark.crypto.getSignature"></a>

#### getSignature

```python
def getSignature(tx, privateKey, **options)
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

<a id="dposlib.ark.crypto.getSignatureFromBytes"></a>

#### getSignatureFromBytes

```python
def getSignatureFromBytes(data, privateKey)
```

Generate signature from data using private key.

**Arguments**:

- `data` _bytes_ - bytes sequence.
- `privateKey` _str_ - private key as hex string.
  

**Returns**:

- `hex` - signature.

<a id="dposlib.ark.crypto.verifySignature"></a>

#### verifySignature

```python
def verifySignature(value, publicKey, signature)
```

Verify signature.

**Arguments**:

- `value` _str_ - value as hex string.
- `publicKey` _str_ - public key as hex string.
- `signature` _str_ - signature as hex string.
  

**Returns**:

- `bool` - True if signature matches the public key.

<a id="dposlib.ark.crypto.verifySignatureFromBytes"></a>

#### verifySignatureFromBytes

```python
def verifySignatureFromBytes(data, publicKey, signature)
```

Verify signature.

**Arguments**:

- `data` _bytes_ - data.
- `publicKey` _str_ - public key as hex string.
- `signature` _str_ - signature as hex string.
  

**Returns**:

- `bool` - True if signature matches the public key.

<a id="dposlib.ark.crypto.getId"></a>

#### getId

```python
def getId(tx)
```

Generate transaction id.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
  

**Returns**:

- `hex` - id.

<a id="dposlib.ark.crypto.getIdFromBytes"></a>

#### getIdFromBytes

```python
def getIdFromBytes(data)
```

Generate data id.

**Arguments**:

- `data` _bytes_ - data as bytes sequence.
  

**Returns**:

- `hex` - id.

<a id="dposlib.ark.crypto.getBytes"></a>

#### getBytes

```python
def getBytes(tx, **options)
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

<a id="dposlib.ark.crypto.checkTransaction"></a>

#### checkTransaction

```python
def checkTransaction(tx, secondPublicKey=None, multiPublicKeys=[])
```

Verify transaction validity.

**Arguments**:

- `tx` _dict or Transaction_ - transaction object.
- `secondPublicKey` _str_ - second public key to use if needed.
- `multiPublicKeys` _list_ - owners public keys (sorted according to
  associated type-4-tx asset).
  

**Returns**:

- `bool` - True if transaction is valid.

