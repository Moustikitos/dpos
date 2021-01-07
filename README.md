> `dposlib` package aims to provide a simple API to ARK blockchain and forks.

[![Build Status](https://travis-ci.com/Moustikitos/dpos.svg?branch=master)](https://travis-ci.com/Moustikitos/dpos)
[![Sphinx Status](https://readthedocs.org/projects/dpos/badge/?version=latest)](https://dpos.readthedocs.io/en/latest/?badge=latest)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/dposlib.svg)](https://pypi.python.org/pypi/dposlib)
[![PyPI version shields.io](https://img.shields.io/pypi/v/dposlib.svg)](https://pypi.python.org/pypi/dposlib)
[![GitHub release](https://img.shields.io/github/tag/Moustikitos/dpos.svg)](https://GitHub.com/Moustikitos/dpos/tags)
[![Downloads](https://pepy.tech/badge/dposlib/week)](https://pepy.tech/project/dposlib)

### Support this project
 
 [![Liberapay receiving](https://img.shields.io/liberapay/goal/Toons?logo=liberapay)](https://liberapay.com/Toons/donate)
 
 [Buy &#1126;](https://bittrex.com/Account/Register?referralCode=NW5-DQO-QMT) and:
 
   * [X] Send &#1126; to `AUahWfkfr5J4tYakugRbfow7RWVTK35GPW`
   * [X] Vote `arky` on [Ark blockchain](https://explorer.ark.io) and [earn &#1126; weekly](http://arky-delegate.info/arky)

# Quick View

## Ubuntu dependencies installation

```bash
sudo apt-get install python python-dev python3 python3-dev
sudo apt-get install python-setuptools python3-setuptools
sudo apt-get install python-pip python3-pip
```

## Available network

  - Ark-core 3.0 (`API`+ transaction type `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9` & `10`)
    * [X] devnet : `dark`
  - Ark-core 2.6 (`API`+ transaction type `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9` & `10`)
    * [X] mainet : `ark`
    * [X] devnet : `dark2`
  - Ark forks (`API`+ transaction type `0`, `1`, `2` & `3`)
    + [x] Internet of People
      * [X] mainet : `iop`
      * [X] devnet : `diop`
    + [x] Ripa : `ripa`
    + [x] Phantom : `phantom`
    + [x] Qredit : `qredit`

## Main features

### An intuitive REST API
```python
>>> from dposlib import rest
>>> rest.use("dark")
>>> # ~/api/delegates/darktoons endpoint
>>> rest.GET.api.delegates.darktoons()
{'data': {'username': 'darktoons', 'address': 'D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk', 'publicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933', 'votes': 9385785081642, 'rank': 45, 'blocks': {'produced': 32015, 'last': {'id': '9d5085e503e09c656152b541bc243155f560347aa8b377d3f2f9a1cb71900d90', 'height': 2544602, 'timestamp': {'epoch': 69406864, 'unix': 1559508064, 'human': '2019-06-02T20:41:04.000Z'}}}, 'production': {'approval': 0.07}, 'forged': {'fees': 14640580130, 'rewards': 6403000000000, 'total': 6417640580130}}}
>>> # ~/api/node/fees endpoint
>>> rest.GET.api.node.fees()
{'meta': {'days': 7}, 'data': [{'type': '0', 'min': '200000', 'max': '10000000', 'avg': '1089596', 'sum': '14887144978', 'median': '460000'}, {'type': '1', 'min': '500000000', 'max': '500000000', 'avg': '500000000', 'sum': '313500000000', 'median': '500000000'}, {'type': '3', 'min': '10000000', 'max': '100000000', 'avg': '58541781', 'sum': '1756253430', 'median': '61114510'}]}
```

### Fast way to interact with blockchain
```python
>>> import dposlib
>>> rest.use("dark")
>>> # send 1 token to D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk with a simple message
>>> tx = dposlib.core.transfer(1, "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk", "message")
>>> # sign tx with secret and [optional second secret]
>>> tx.finalize("first secret", "second secret")
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "fee": 1090241,
  "id": "1e967879eb134712afd2b2a606be8460468b80aab857fa99a88cf8da0d72bd5d",
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
  "signSignature": "3045022100a8dd9c50b18002bd6f8ffe9f1c0700cafb95de18670b48fa76afd85c3003a2d202200a1cc102c13857a38d8311a5c80a9222329f0c53f3305c70c91979efd5288d21",
  "signature": "304402206576aee7893f3c038d58a6def5180881077531c4b1ebe87e835da2dbe40d0670022064ae37be3f160b0c969459e06912ee619997ccf303e6d919135cdf594a74b77d",
  "timestamp": 69407340,
  "type": 0,
  "vendorField": "message"
}
>>> # broadcast transaction
>>> rest.POST.api.transactions(transactions=[tx])
{'data': {'accept': ['1e967879eb134712afd2b2a606be8460468b80aab857fa99a88cf8da0d72bd5d'], 'broadcast': ['1e967879eb134712afd2b2a606be8460468b80aab857fa99a88cf8da0d72bd5d'], 'excess': [], 'invalid': []}}
```

### Network API

```python
>>> import dposlib
>>> rest.use("ark")
>>> dlgt = dposlib.core.api.Delegate("arky")  # get delegate by username
>>> dlgt.forged
{'fees': 3294.7, 'forged': 227230.7, 'rewards': 223936.0}
>>> dlgt.address
'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE'
>>> blk = dlgt.lastBlock  # get last forged block
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

<!-- ### Ledger Nano S integration

If you want to use `dposlib.ark.ldgr` module, you need to install ledgerblue
package and its dependencies:

```bash
sudo apt-get install libudev-dev libusb-1.0.0-dev
pip install ledgerblue
```

```python
>>> rest.use("dark")
>>> # 1,0,0 = devnet, account, index
>>> ldg = dposlib.core.api.NanoS(1, 0, 0)
>>> ldg
{
  "address": "DEVx3osw9Rj1wZhoUf2dMbPmmUN9P3XFpb",
  "balance": 69.9939675,
  "isDelegate": true,
  "publicKey": "025993c687f1e3418e0aa47b6ab091e414b51c45b32a107745c01c124652112c7a",
}
>>> ldg.derivationPath
"44'/1'/1'/0'/0"
>>> ldg.send(1, "DGuuCwJYoEheBAC4PZTBSBasaDHxg2e6j7")
```
<img src="https://raw.githubusercontent.com/Moustikitos/dpos/master/doc/static/ledger_confirm.png" />

```python
{'data': {'accept': ['7445b0748aae8778bcd73d2ca40d8cc19ffee7b68ea89f05e1934b96dd73ed2f'], 'broadcast': ['7445b0748aae8778bcd73d2ca40d8cc19ffee7b68ea89f05e1934b96dd73ed2f'], 'excess': [], 'invalid': []}}
>>> ldg.upVote("darktoons")
```
<img src="https://raw.githubusercontent.com/Moustikitos/dpos/master/doc/static/ledger_confirm.png" />

```python
{'data': {'accept': ['c13791c8ca0cbcd8ef62a722a4a157fa6aa97a86770f988d9a6dc3234b562bc2'], 'broadcast': ['c13791c8ca0cbcd8ef62a722a4a157fa6aa97a86770f988d9a6dc3234b562bc2'], 'excess': [], 'invalid': []}}
>>> dposlib.core.api.NanoS.fromDerivationPath("44'/1'/0'/0/0")
{
  "address": "DDC7kWToyvfKa8dvRTXitr7o5FHMVKtBve",
  "balance": 95.20477813,
  "publicKey": "038473178d89988b1f8428efe758b99ebf1d49c47b679f3f4a9cdc0829fa6ece2b",
  "vote": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933"
}
```
 -->

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

### 0.1.3
  - [x] REST requests header bugfix (ubuntu)

### 0.1.4
  - [x] Python 2.x compatibility fix
  - [x] dposlib.core.Transaction.sign does not set fees anymore
  - [x] dposlib.core.Transaction.finalize set fees before signature
  - [x] dposlib.core.Transaction fee management improved

### 0.1.5
  - [x] compatibility with both ark-core v2 devnet and mainnet

### 0.1.6
  - [x] Ark-core v 2.1.x compatibility

### 0.1.7
  - [x] added `transaction` and `rest` MarkDown documentation files
  - [x] dposlib.core.api is both python 2.x and 3.x compliant
  - [x] added Webhook api (experimental)
  - [x] fee data initialisation improvement
  - [x] transaction broadcasting improvement
  - [x] peer selection improvement
  - [x] Lisk blockchain and forks developpement frozen

### 0.1.8
  - [x] added ark v2.4 compatibility
  - [x] api wallet link using getpass library
  - [x] added ledger nano S support (transaction type 0, 1, 2 & 3)
  - [x] peer selection now checks syncing status

### 0.1.9
  - [x] [travis-ci](https://travis-ci.com) integration
  - [x] dposlib.core.Transaction interface improvement
  - [x] Ark v1 and v2 cross-dependency removed
  - [x] offline work feature added

### 0.2.0
  - [x] ark.v2 api improvement
  - [x] dposlib.util.misc module improvement
  - [x] upVote/downVote bugfix

### 0.2.1
  - [x] added `lisk` blockchain
  - [x] added `shift`, `t.shift` and `qredit` network
  - [x] added .cold data in package distribution
  - [x] transaction types `0`, `1` and `3` added to lisk.v09 network
  - [x] python 2.x compliancy for util.data package

### 0.2.2 
  - [x] Ark v2.5 headers fix
  - [x] Ark v2.5 BigInt fix
  - [x] packaging improvement
  - [x] rest `returnKey` behaviour improvement

### 0.3.0
  - [x] `flake8` compliancy
  - [x] Ark 2.6 compatibility
  - [x] removed package resources dependencies
  - [x] `ecdsa` lib replaced by builtin `secp256k1`
  - [x] added [Iop](https://iop.global/) mainnet and devnet
  - [x] Lisk and forks dev stopped
  - [x] `ldgr` import now optional
  - [x] sphinx doc added

### 0.3.1
  - [x] multisignature client-server api

### 0.3.2
  - [x] better `vendorFieldHex` field  handling
  - [x] `dposlib.blockchain.Transaction` behaviour improvement
  - [x] tx versioning defined in `net` module
  - [x] bridge for ark-core 2.5 and 2.6

### 0.3.3
  - [x] offline start fixed
  - [x] `api.Wallet` fixed
  - [x] added pythonic `datetime` attribute to `Transaction` class

### 0.3.4
  - [x] removed `requests` dependency
  - [x] multisignature api and app run as system services

### 0.3.5 [current work](https://github.com/Moustikitos/dpos/archive/master.zip)
  - [ ] Ark-core v 3.0.x compliancy
  - [ ] `entity` and `business` transactions implementation

## TODO
  - [ ] custom transaction implementation
