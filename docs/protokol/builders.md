<a id="dposlib.protokol.builders"></a>

# dposlib.protokol.builders

<a id="dposlib.protokol.builders.nftRegisterCollection"></a>

#### nftRegisterCollection

```python
def nftRegisterCollection(name, desc, supply, schema, *issuers, **meta)
```

Build a NFT collection registration transaction.

**Arguments**:

- `name` _str_ - NFT name.
- `desc` _str_ - NFT description.
- `supply` _int_ - NFT maximum supply.
- `schema` _dict_ - NFT json schema.
- `issuers` _*args_ - list of public keys allowed to issue the NFT.
- `meta` _**kwargs_ - NFT metadata.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.protokol.builders.nftCreate"></a>

#### nftCreate

```python
def nftCreate(collectionId, attributes, address=None)
```

Build a NFT mint transaction.

**Arguments**:

- `collectionId` _str_ - NFT collection id.
- `attributes` _dict_ - NFT attributes matching defined schema.
- `address` _str_ - recipient address.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.protokol.builders.nftTransfer"></a>

#### nftTransfer

```python
def nftTransfer(address, *ids)
```

Build a NFT transfer transaction.

**Arguments**:

- `address` _str_ - recipient address.
- `ids` _list_ - list of NFT id to send (maximum=10).
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

<a id="dposlib.protokol.builders.nftBurn"></a>

#### nftBurn

```python
def nftBurn(txid)
```

Build a NFT burn transaction.

**Arguments**:

- `txid` _str_ - NFT mint transaction id.
  

**Returns**:

- `dposlib.ark.tx.Transaction` - orphan transaction.

