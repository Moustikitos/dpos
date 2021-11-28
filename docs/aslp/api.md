<a id="dposlib.aslp.api"></a>

# dposlib.aslp.api

This module provides both [Ark API](../ark/api.md) and [ASLP API](
    https://aslp.qredit.dev
) interface.

## Write endpoints

Below a request to `https://aslp.qredit.dev/api/tokens` endpoint:

```python
>>> from dposlib import rest
>>> rest.use("aslp")
>>> from dposlib.aslp.api import GET
>>> GET.api.status()
{'downloadedBlocks': 18333367, 'scannedBlocks': None, 'status': 200}
>>> tokens = GET.api.tokens()
>>> tokens[0]["tokenDetails"]
{
    'schema_version': 15,
    'ownerAddress': 'ARKQXzHvEWXgfCgAcJWJQKUMus5uE6Yckr',
    'tokenIdHex': '8259ce077b1e767227e5e0fce590d26d',
    'versionType': 1,
    'genesis_timestamp': '2021-11-20T09:23:44.000Z',
    'genesis_timestamp_unix': 1637400224,
    'symbol': 'BARK',
    'name': 'bARK',
    'documentUri': 'ipfs://QmdFtN96SxKjPQwMGN4Cv51XCvvAwrME1rt95PPFbJmexQ',
    'decimals': 0,
    'genesisQuantity': '420000000069',
    'pausable': False,
    'mintable': False
}
```

## Use `keyword` arguments

Below a request to `https://aslp.qredit.dev/api/vendor_aslp1_genesis` endpoint:

```python
>>> GET.api.vendor_aslp1_genesis(
...   decimals="2",
...   symbol="TTK",
...   name="Toon's token",
...   uri="ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq",
...   quantity="250000",
...   notes="This is for demo purpose only.",
...   pausable="true",
...   mintable="true"
... )
{
  'aslp1': {
    'tp': 'GENESIS',
    'de': '2',
    'sy': 'TTK',
    'na': "Toon's token",
    'qt': '25000000',
    'du': 'ipfs://bafkreigfxalrf52xm5ecn4lorfhiocw4x5cxpktnkiq3atq6jp2elktobq',
    'no': 'This is for demo purpose only.'
  },
  'status': 200
}
```

