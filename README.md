# `dposlib` Quick View

`dposlib` package aims to provide a simple API to ARK blockchain and forks.

## Support this project

  * [X] Send &#1126; to `AUahWfkfr5J4tYakugRbfow7RWVTK35GPW`
  * [X] Vote `arky` on [Ark blockchain](https://explorer.ark.io) and [earn &#1126; weekly](http://dpos.arky-delegate.info/arky)

## Overview

**Import REST API**
```python
>>> from dposlib import rest
>>> rest.use("dark")
```

**Bake Transaction:**
```python
>>> from dposlib.blockchain import Transaction
>>> tx = Transaction(
... amount=100000000,
... recipientId="DRgh1n8oyGHDE6xXVq4yhh3sSajAr7uHJY",
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

  - [x] Ark
    * mainet : `ark`
    * devnet : `dark`
    * forks
      - [x] Kapu : `kapu`
      - [x] Persona : `prs`
      - [x] Ripa : `ripa`
      - [x] Phantom : `xph`

## Network API

```python
>>> rest.use("ark")
>>> dlgt = dposlib.core.api.Delegate("arky") # get delegate by username
>>> dlgt.forged()
{'fees': 3294.7, 'forged': 227230.7, 'rewards': 223936.0}
>>> dlgt.address
'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE'
>>> blk = dlgt.lastBlock() # get last forged block
>>> blk
{
  "blockSignature": "304402200a496a628c2741537538f0492f9d683d3c4f1b30c8dd03c33ad8fbe79d08b6eb02206cdec7e1210db53a3ca22da30912479ff3644d3a1ed1d878417d5965f34dfd6d",
  "confirmations": 68,
  "generatorId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "generatorPublicKey": "030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d60a15e9",
  "height": 5862354,
  "id": "1894085440657345411",
  "numberOfTransactions": 0,
  "payloadHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "payloadLength": 0,
  "previousBlock": "11181074894913507025",
  "reward": 2.0,
  "timestamp": 47535768,
  "totalAmount": 0.0,
  "totalFee": 0.0,
  "totalForged": 2.0,
  "version": 0
}
>>> blk.transactions()
[]
>>> wlt = dposlib.core.api.Wallet(dlgt.address) # get wallet by address
>>> wlt.balance
2537.42979112
>>> for elem in [(tx["recipientId"], tx["amount"]) for tx in wlt.lastTransactions(2)]:
...     print(elem)
...
('AHMXV6UdkVxsTwMqeoeqdpotRRmGZZaAtj', 0.08403461)
('AUahWfkfr5J4tYakugRbfow7RWVTK35GPW', 329.32420472)
>>> wlt.link("secret passphrase here")
>>> wlt.send(1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE")
{'transactionIds': ['bbce72e7a76f5f71209c8ab29b4b4299a409241dfc77835150459a34bd5a5c16'], 'success': True}
```

  - [x] Ark v1
  - [x] Ark v2

## Install

## Version

### 0.1.0
  - [x] First rebrand

### 0.1.1
  - [x] ARK packaging improvement (`v1` and `v2`)
  - [x] LISK packaging improvement (`v09` and `v10`)
  - [x] ARK dynamicFee implementation
  - [x] Network API created

### 0.1.2
  - [x] Packaging improvement

### 0.1.3 : available on [PyPi](https://pypi.org/project/dposlib/)
  - [x] REST requests header bugfix (ubuntu)

### 0.1.4
  - [x] Python 2.x compatibility fix
  - [x] dposlib.core.Transaction.sign does not set fees anymore
  - [x] dposlib.core.Transaction.finalize set fees before signature
  - [x] dposlib.core.Transaction fee management improved

### 0.1.5
  - [x] compatibility with both ark-core v2 devnet and mainnet

### 0.1.6 :
  - [x] Ark-core v 2.1.x compatibility

### 0.1.7 :
  - [X] added `transaction` and `rest` MarkDown documentation files
  - [x] dposlib.core.api is both python 2.x and 3.x compliant
  - [x] added Webhook api (experimental)
  - [x] fee data initialisation improvement
  - [x] transaction broadcasting improvement
  - [x] peer selection improvement
  - [x] Lisk blockchain and forks developpement frozen

### 0.1.8 [current work](https://github.com/Moustikitos/dpos/archive/master.zip)

## TODO
  - [ ] integrate LedgerBlue Nano S use
  - [ ] doc writing
  - [ ] unittest
  - [ ] wallet
  - [ ] CLI
 