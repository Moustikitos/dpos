# `dposlib`

`dposlib` package aims to provide a simple API to link major DPOS blockchain.

## Overview

**Import REST API**
```python
>>> from dposlib import rest
>>> rest.use("dark2")
```

**Bake Transaction:**
```python
>>> from dposlib.blockchain import Transaction
>>> tx = Transaction(
... amount=100000000,
... recipientId="ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
... secret="secret",
... secondSecret="secondSecret")
>>> tx.finalize()
>>> tx
{
  "amount": 100000000,
  "fee": 1830000,
  "id": "5a90ea87fb8848c3402e5d6da5d34651eee01124387aa4f499c84621e03dd791",
  "recipientId": "DRgh1n8oyGHDE6xXVq4yhh3sSajAr7uHJY",
  "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
  "signSignature": "3045022100f297bf2241eb1603c4e91552416bbd900f1335684d3bb8751a043b5ae4569948022067c166322df1374222589d81b4ea52d56d93db8eab7be59a258420cbc6217360",
  "signature": "304402205e609776d7d04a659ab8057e269c26e8b611ed4952ffb6b1af9c9bca19a9e3c50220755b8e2a10783bab0e7da95229e358d8e9e4628241a39640869fb8bf856a953a",
  "timestamp": 45690392,
  "type": 0
}
```

**Broadcast transaction**
```python
>>> rest.POST.api.transactions(transactions=[tx])
{'data': {'broadcast': ['5a90ea87fb8848c3402e5d6da5d34651eee01124387aa4f499c84621e03dd791'], 'excess': [], 'invalid': [], 'accept': []}}
```

## Available network

  - [x] ARK
    * mainet : `ark`
    * devnet : `dark2`
  - [x] KAPU : `kapu`
  - [x] Local World Forwarder :
    * mainet : `lwf`
    * testnet : `tlwf`
  - [x] Persona : `prs`
  - [x] Ripa : `ripa`
  - [x] Shift : 
    * mainet : `shift`
    * testnet : `tshift`

## Version

### 0.1.0 : first release

### 0.1.1

 - [x] ARK packaging improvement (`v1` and `v2`)
 - [x] ARK dynamicFee implementation
 - [x] readonly wallet

TODO
  - [ ] write `api` for each network package
  - [ ] unittest
  - [ ] wallet
  - [ ] CLI
  - [ ] DOC
