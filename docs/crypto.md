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

<a name="dposlib.ark.ldgr"></a>
# dposlib.ark.ldgr

This module contains functions to interoperate with [Ledger](
    https://ledger.com
) hard wallet.

<a name="dposlib.ark.ldgr.parseBip44Path"></a>
#### parseBip44Path

```python
parseBip44Path(path)
```

Parse a [BIP44](
https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
) derivation path.

**Arguments**:

- `path` _str_ - the derivation path

**Returns**:

  parsed bip44 path as bytes

<a name="dposlib.ark.ldgr.buildPukApdu"></a>
#### buildPukApdu

```python
buildPukApdu(dongle_path)
```

Generate apdu to get public key from ledger key.

**Arguments**:

- `dongle_path` _bytes_ - value returned by
  [`dposlib.ark.ldgr.parseBip44Path`](
  crypto.md#parsebip44path
  )

**Returns**:

  public key apdu data as bytes

<a name="dposlib.ark.ldgr.getPublicKey"></a>
#### getPublicKey

```python
getPublicKey(path=None, debug=False)
```

Compute the public key associated to a derivation path.

**Arguments**:

- `path` _str_ - derivation path
- `debug` _bool_ - flag to activate debug messages from ledger key

**Returns**:

  hexadecimal compressed publicKey

<a name="dposlib.ark.ldgr.signMessage"></a>
#### signMessage

```python
signMessage(msg, path=None, schnorr=True, debug=False)
```

Compute schnorr or ecdsa signature of msg according to derivation path.

**Arguments**:

- `msg` _str or bytes_ - transaction as dictionary
- `path` _str_ - derivation path
- `schnorr` _bool_ - use schnorr signature if True else ecdsa
- `debug` _bool_ - flag to activate debug messages from ledger key

<a name="dposlib.ark.ldgr.signTransaction"></a>
#### signTransaction

```python
signTransaction(tx, path=None, schnorr=True, debug=False)
```

Append sender public key and signature into transaction according to
derivation path.

**Arguments**:

- `tx` _dposlib.blockchain.tx.Transaction_ - transaction
- `path` _str_ - derivation path
- `schnorr` _bool_ - use schnorr signature if True else ecdsa
- `debug` _bool_ - flag to activate debug messages from ledger key

