<a id="dposlib.aslp.builders"></a>

# dposlib.aslp.builders

ASLP transaction builders. See [ASLP API](https://aslp.qredit.dev) for more
information.

  - ASLP1 token is an ERC20-equivalent-smartbridge-embeded token.
  - ASLP2 token is an NFT-equivalent-smartbridge-embeded token.

```python
>>> t = dposlib.core.aslpGenesis(
...    2, "TTK", "Toon's token", 250000,
...    du="ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq",
...    no="For testing purpose only.", pa=True, mi=True
... )
>>> t.vendorField
'{"aslp1":{"tp":"GENESIS","de":"2","sy":"TTK","na":"Toon\'s token","qt":"25000'
'000","du":"ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq'
'","no":"For testing purpose only."}}'
>>>
>>> t.finalize("secret passphrase")
>>> print(t)
{
  "version": 2,
  "amount": 100000000,
  "asset": {},
  "fee": 5000000,
  "id": "ff2c7e5300a1457b289ced0644ec36fe073958d01d2b2b9976dbcff21064781b",
  "network": 23,
  "nonce": 1,
  "recipientId": "ARKQXzHvEWXgfCgAcJWJQKUMus5uE6Yckr",
  "senderId": "AdzCBJt2F2Q2RYL7vnp96QhTeGdDZNZGeJ",
  "senderPublicKey":
    "03aacac6c98daaf3d433fe90e9295ce380916946f850bcdc6f6880ae6503ca1e40",
  "signature":
    "fa754a2966d44197c08093263e8a1287fce7ab0c05dcccc4e0f7a0f00a1a781527d911629"
    "c67c58dea6873d8841e37c1057d247813b06e47cf3b59033ed7bc91",
  "timestamp": 147979327,
  "type": 0,
  "typeGroup": 1,
  "vendorField":
    "{\"aslp1\":{\"tp\":\"GENESIS\",\"de\":\"2\",\"sy\":\"TTK\",\"na\":\"Toon'"
    "s token\",\"qt\":\"25000000\",\"du\":\"ipfs://bafkreigfxalrf52xm5ecn4lorf"
    "hiocw4x5cxpktnkiq3atq6jp2elktobq\",\"no\":\"For testing purpose only.\"}}"
}
>>> dposlib.core.broadcastTransactions(t)
{
  'data': {
    'accept': [],
    'broadcast': [],
    'excess': [],
    'invalid': [
      'ff2c7e5300a1457b289ced0644ec36fe073958d01d2b2b9976dbcff21064781b'
    ]
  }, 'errors': {
    'ff2c7e5300a1457b289ced0644ec36fe073958d01d2b2b9976dbcff21064781b': {
      'type': 'ERR_APPLY',
      'message':
        'AdzCBJt2F2Q2RYL7vnp96QhTeGdDZNZGeJ#1 1064781b Transfer v2 cannot be a'
        'pplied: Insufficient balance in the wallet.'
    }
  },
  'status': 200
}
```

<a id="dposlib.aslp.builders.aslpGenesis"></a>

#### aslpGenesis

```python
def aslpGenesis(de, sy, na, qt, du=None, no=None, pa=False, mi=False)
```

Build a aslp1 genesis transaction.

**Arguments**:

- `de` _int_ - decimal number.
- `sy` _str_ - token symbol.
- `na` _str_ - token name.
- `qt` _int_ - maximum supply.
- `du` _str_ - document URI.
- `no` _str_ - token notes.
- `pa` _bool_ - pausable token ?
- `mi` _bool_ - mintable token ?
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpBurn"></a>

#### aslpBurn

```python
def aslpBurn(tkid, qt, no=None)
```

Build a aslp1 burn transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `qt` _int_ - quantity to burn.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpMint"></a>

#### aslpMint

```python
def aslpMint(tkid, qt, no=None)
```

Build a aslp1 mint transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `qt` _int_ - quantity to burn.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpSend"></a>

#### aslpSend

```python
def aslpSend(address, tkid, qt, no=None)
```

Build a aslp1 send transaction.

**Arguments**:

- `address` _str_ - recipient wallet address.
- `tkid` _str_ - token id.
- `qt` _int_ - quantity to burn.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpPause"></a>

#### aslpPause

```python
def aslpPause(tkid, no=None)
```

Build a aslp1 pause transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpResume"></a>

#### aslpResume

```python
def aslpResume(tkid, no=None)
```

Build a aslp1 resume transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpNewOwner"></a>

#### aslpNewOwner

```python
def aslpNewOwner(address, tkid, no=None)
```

Build a aslp1 owner change transaction.

**Arguments**:

- `address` _str_ - new owner wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpFreeze"></a>

#### aslpFreeze

```python
def aslpFreeze(address, tkid, no=None)
```

Build a aslp1 freeze transaction.

**Arguments**:

- `address` _str_ - frozen wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslpUnFreeze"></a>

#### aslpUnFreeze

```python
def aslpUnFreeze(address, tkid, no=None)
```

Build a aslp1 unfreeze transaction.

**Arguments**:

- `address` _str_ - unfrozen wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp1
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2Genesis"></a>

#### aslp2Genesis

```python
def aslp2Genesis(sy, na, du=None, no=None, pa=False)
```

Build a aslp2 genesis transaction.

**Arguments**:

- `sy` _str_ - token symbol.
- `na` _str_ - token name.
- `du` _str_ - URI.
- `no` _str_ - token notes.
- `pa` _bool_ - pausable token ?
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2Pause"></a>

#### aslp2Pause

```python
def aslp2Pause(tkid, no=None)
```

Build a aslp2 pause transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2Resume"></a>

#### aslp2Resume

```python
def aslp2Resume(tkid, no=None)
```

Build a aslp2 resume transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2NewOwner"></a>

#### aslp2NewOwner

```python
def aslp2NewOwner(address, tkid, no=None)
```

Build a aslp2 owner change transaction.

**Arguments**:

- `address` _str_ - new owner wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2AuthMeta"></a>

#### aslp2AuthMeta

```python
def aslp2AuthMeta(address, tkid, no=None)
```

Build a aslp2 meta change authorization transaction.

**Arguments**:

- `address` _str_ - authorized wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2RevokeMeta"></a>

#### aslp2RevokeMeta

```python
def aslp2RevokeMeta(address, tkid, no=None)
```

Build a aslp2 meta change revokation transaction.

**Arguments**:

- `address` _str_ - revoked wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2Clone"></a>

#### aslp2Clone

```python
def aslp2Clone(tkid, no=None)
```

Build a aslp2 clone transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2AddMeta"></a>

#### aslp2AddMeta

```python
def aslp2AddMeta(tkid, na, dt, ch=None)
```

Build a aslp2 metadata edition transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `na` _str_ - name of the metadata info.
- `dt` _str_ - data of metadata.
- `ch` _int_ - chunk number.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

<a id="dposlib.aslp.builders.aslp2VoidMeta"></a>

#### aslp2VoidMeta

```python
def aslp2VoidMeta(tkid, tx)
```

Build a aslp2 metadata cleaning transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `tx` _str_ - transaction id of metadata to void.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate aslp2
  `vendorField`.

