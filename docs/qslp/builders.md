<a id="dposlib.qslp.builders"></a>

# dposlib.qslp.builders

QSLP transaction builders. See [QSLP API](https://aslp.qredit.dev) for more
information.

  - QSLP1 token is an ERC20-equivalent-smartbridge-embeded token.
  - QSLP2 token is an NFT-equivalent-smartbridge-embeded token.

```python
>>> t = dposlib.core.qslpGenesis(
...    2, "TTK", "Toon's token", 250000,
...    du="ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq",
...    no="For testing purpose only.", pa=True, mi=True
... )
>>> t.vendorField
'{"aslp1":{"tp":"GENESIS","de":"2","sy":"TTK","na":"Toon\'s token","qt":"25000\
000","du":"ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq"\
,"no":"For testing purpose only."}}'
>>>
```

<a id="dposlib.qslp.builders.qslpGenesis"></a>

#### qslpGenesis

```python
def qslpGenesis(de, sy, na, qt, du=None, no=None, pa=False, mi=False)
```

Build a QSLP1 genesis transaction.

**Arguments**:

- `de` _int_ - decimal number.
- `sy` _str_ - token symbol.
- `na` _str_ - token name.
- `qt` _int_ - maximum supply.
- `du` _str_ - URI.
- `no` _str_ - token notes.
- `pa` _bool_ - pausable token ?
- `mi` _bool_ - mintable token ?
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpBurn"></a>

#### qslpBurn

```python
def qslpBurn(tkid, qt, no=None)
```

Build a QSLP1 burn transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `qt` _int_ - quantity to burn.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpMint"></a>

#### qslpMint

```python
def qslpMint(tkid, qt, no=None)
```

Build a QSLP1 mint transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `qt` _int_ - quantity to burn.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpSend"></a>

#### qslpSend

```python
def qslpSend(address, tkid, qt, no=None)
```

Build a QSLP1 send transaction.

**Arguments**:

- `address` _str_ - recipient wallet address.
- `tkid` _str_ - token id.
- `qt` _int_ - quantity to burn.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpPause"></a>

#### qslpPause

```python
def qslpPause(tkid, no=None)
```

Build a QSLP1 pause transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpResume"></a>

#### qslpResume

```python
def qslpResume(tkid, no=None)
```

Build a QSLP1 resume transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpNewOwner"></a>

#### qslpNewOwner

```python
def qslpNewOwner(address, tkid, no=None)
```

Build a QSLP1 owner change transaction.

**Arguments**:

- `address` _str_ - new owner wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpFreeze"></a>

#### qslpFreeze

```python
def qslpFreeze(address, tkid, no=None)
```

Build a QSLP1 freeze transaction.

**Arguments**:

- `address` _str_ - frozen wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslpUnFreeze"></a>

#### qslpUnFreeze

```python
def qslpUnFreeze(address, tkid, no=None)
```

Build a QSLP1 unfreeze transaction.

**Arguments**:

- `address` _str_ - unfrozen wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP1
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2Genesis"></a>

#### qslp2Genesis

```python
def qslp2Genesis(sy, na, du=None, no=None, pa=False)
```

Build a QSLP2 genesis transaction.

**Arguments**:

- `sy` _str_ - token symbol.
- `na` _str_ - token name.
- `du` _str_ - URI.
- `no` _str_ - token notes.
- `pa` _bool_ - pausable token ?
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2Pause"></a>

#### qslp2Pause

```python
def qslp2Pause(tkid, no=None)
```

Build a QSLP2 pause transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2Resume"></a>

#### qslp2Resume

```python
def qslp2Resume(tkid, no=None)
```

Build a QSLP2 resume transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2NewOwner"></a>

#### qslp2NewOwner

```python
def qslp2NewOwner(address, tkid, no=None)
```

Build a QSLP2 owner change transaction.

**Arguments**:

- `address` _str_ - new owner wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2AuthMeta"></a>

#### qslp2AuthMeta

```python
def qslp2AuthMeta(address, tkid, no=None)
```

Build a QSLP2 meta change authorization transaction.

**Arguments**:

- `address` _str_ - authorized wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2RevokeMeta"></a>

#### qslp2RevokeMeta

```python
def qslp2RevokeMeta(address, tkid, no=None)
```

Build a QSLP2 meta change revokation transaction.

**Arguments**:

- `address` _str_ - revoked wallet address.
- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2Clone"></a>

#### qslp2Clone

```python
def qslp2Clone(tkid, no=None)
```

Build a QSLP2 clone transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `no` _str_ - token notes.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2AddMeta"></a>

#### qslp2AddMeta

```python
def qslp2AddMeta(tkid, na, dt, ch=None)
```

Build a QSLP2 metadata edition transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `na` _str_ - name of the metadata info.
- `dt` _str_ - data of metadata.
- `ch` _int_ - chunk number.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

<a id="dposlib.qslp.builders.qslp2VoidMeta"></a>

#### qslp2VoidMeta

```python
def qslp2VoidMeta(tkid, tx)
```

Build a QSLP2 metadata cleaning transaction.

**Arguments**:

- `tkid` _str_ - token id.
- `tx` _str_ - transaction id of metadata to void.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction with appropriate QSLP2
  `vendorField`.

