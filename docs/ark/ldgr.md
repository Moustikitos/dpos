<a id="dposlib.ark.ldgr"></a>

# dposlib.ark.ldgr

This module contains functions to interoperate with [Ledger](
    https://ledger.com
) hard wallet.

<a id="dposlib.ark.ldgr.parseBip44Path"></a>

#### parseBip44Path

```python
def parseBip44Path(path)
```

Parse a [BIP44](
https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
) derivation path.

**Arguments**:

- `path` _str_ - the derivation path.
  

**Returns**:

- `bytes` - parsed bip44 path.

<a id="dposlib.ark.ldgr.getPublicKey"></a>

#### getPublicKey

```python
def getPublicKey(path=None, debug=False)
```

Compute the public key associated to a derivation path.

**Arguments**:

- `path` _str_ - derivation path.
- `debug` _bool_ - flag to activate debug messages from ledger key.
  

**Returns**:

- `hex` - secp256k1-compressed publicKey.

<a id="dposlib.ark.ldgr.signMessage"></a>

#### signMessage

```python
def signMessage(msg, path=None, schnorr=True, debug=False)
```

Compute schnorr or ecdsa signature of msg according to derivation path.

**Arguments**:

- `msg` _str or bytes_ - message to sign.
- `path` _str_ - derivation path.
- `schnorr` _bool_ - use schnorr signature if True else ecdsa.
- `debug` _bool_ - flag to activate debug messages from ledger key.
  

**Returns**:

- `hex` - message signature.

<a id="dposlib.ark.ldgr.signTransaction"></a>

#### signTransaction

```python
def signTransaction(tx, path=None, schnorr=True, debug=False)
```

Append sender public key and signature into transaction according to
derivation path.

**Arguments**:

- `tx` _dposlib.ark.tx.Transaction_ - transaction.
- `path` _str_ - derivation path.
- `schnorr` _bool_ - use schnorr signature if True else ecdsa.
- `debug` _bool_ - flag to activate debug messages from ledger key.
  

**Returns**:

- `hex` - transaction signature. Signature is also added to transaction
  object as `signature` item.

