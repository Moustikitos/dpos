# class `Transaction`

`Transaction` object a center piece of `dposlib` package. It is a python dictionary containing basic functions to interact with a blockchain environement. `Transaction` class is available in `blockchain` sub package.

[A blockchain must be loaded first](rest.md)

Transaction object is available in `dposlib.blockchain` package&nbsp;:

```python
>>> from dposlib import blockchain
```

## Create a transaction

```python
>>> tx = blockchain.Transaction()
```
Default transaction is a `Transfer` transaction (`type = 0`). It is a python dictionary with `__getattr__` and `__setattr__` interface implemented. Only valid transaction fields are allowed trough `Transaction` object interface.
```python
>>> tx
{
  "amount": 0,
  "asset": {},
  "timestamp": 1559492013,
  "type": 0
}
>>> tx.amount = "11000"
>>> tx["amount"]
11000
>>> tx.wrongField = "wrongValue"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\Bruno\GitHub\dpos\dposlib\blockchain\__init__.py", line 174, in __setattr__
    self[attr] = value
  File "C:\Users\Bruno\GitHub\dpos\dposlib\blockchain\__init__.py", line 166, in __setitem__
    raise AttributeError("attribute %s not allowed in transaction class" % item)
AttributeError: attribute wrongField not allowed in transaction class
```

### Available transaction types

The `dposlib.core` module provides transaction builders matching available blockchain transaction types.

```python
>>> dposlib.core.transfer(1, "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk", "vendorField value")
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "timestamp": 69406298,
  "type": 0,
  "vendorField": "vendorField value"
}
>>> dposlib.core.registerSecondSecret("secondSecret")
>>> # or
>>> dposlib.core.registerSecondPublicKey("0292d580f200d041861d78b3de5ff31c6665b7a092ac3890d9132593beb9aa8513")
{
  "amount": 0,
  "asset": {
    "signature": {
      "publicKey": "0292d580f200d041861d78b3de5ff31c6665b7a092ac3890d9132593beb9aa8513"
    }
  },
  "timestamp": 69406435,
  "type": 1
}
>>> dposlib.core.registerAsDelegate("username")
{
  "amount": 0,
  "asset": {
    "delegate": {
      "username": "username"
    }
  },
  "timestamp": 69406518,
  "type": 2
}
>>> dposlib.core.upVote("username")
{
  "amount": 0,
  "asset": {
    "votes": [
      "+02d504380b5b99fb3d839772fad3ef63b5ab1b2239b52a71e88bd96374ef0f5bfd"
    ]
  },
  "timestamp": 69406610,
  "type": 3
}
>>> dposlib.core.downVote("username")
{
  "amount": 0,
  "asset": {
    "votes": [
      "-02d504380b5b99fb3d839772fad3ef63b5ab1b2239b52a71e88bd96374ef0f5bfd"
    ]
  },
  "timestamp": 69406626,
  "type": 3
}
```

## Finalize transaction : the fast way

`dposlib.blockchain.Transaction` class provides a fast and simple way to sign a transaction.

```python
>>> tx = dposlib.core.transfer(1, "DGuuCwJYoEheBAC4PZTBSBasaDHxg2e6j7", "vendorField value")
>>> tx.finalize("secret", "secondSecret")
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "fee": 1089042,
  "id": "0030817df517fc78718ffca8601c745cf879b02c77c7d4a542241c715538dd7c",
  "recipientId": "DGuuCwJYoEheBAC4PZTBSBasaDHxg2e6j7",
  "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
  "signSignature": "304402202e7fae36f102fd4d7274dc9eb1bdf2a4a5098921b1dcae48e591d604373bd629022027f94d8374890fb0a6fa7703de0a96181e4b260672ffc9f1818a11daa57db9fe",
  "signature": "3045022100d5bdac44fe58c90b704ab4b5ef18007e7f77ba26dbfd631a7001c0cd8e71ee5602206f0794ada5cde643e289f71041bd9535635f39813c4f274fd95cd0cfbc08bb90",
  "timestamp": 69408909,
  "type": 0,
  "vendorField": "vendorField value"
}
>>> # fee_included : fee + amount = desired amount spent
>>> tx.finalize("secret", "secondSecret", fee_included=True)
>>> tx
{
  "amount": 98910958,
  "asset": {},
  "fee": 1089042,
  "id": "457361cc4c074dd7f77e89a2fb47263e01791f300299b6fc839d2703383467f3",
  "recipientId": "DGuuCwJYoEheBAC4PZTBSBasaDHxg2e6j7",
  "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
  "signSignature": "304402204e8a0719f49fc119bd0ee0065fd9dec99b945f437dd74fe794d320664bec29fd02203152c6efe95fa73b4bf7179f414560d157d18e67ac86a36b4fa39cfc2c5da4b8",
  "signature": "3045022100a51496456a77b5141bcfb4c78ca524122b037d5aa0fc6b9ae19a279d56dc75fd02203823c284bb3d9f1b497d059c881b7af72b5b6cff7c1c4b4279fcf57f169147f4",
  "timestamp": 69408909,
  "type": 0,
  "vendorField": "vendorField value"
}
>>> # fee can be set manualy
>>> tx.finalize("secret", "secondSecret", fee=200000, fee_included=True)
>>> tx
{
  "amount": 99800000,
  "asset": {},
  "fee": 200000,
  "id": "d112c4183a786e316b016e94f681101ad92658e718034642c51347dce251ed67",
  "recipientId": "DGuuCwJYoEheBAC4PZTBSBasaDHxg2e6j7",
  "senderId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933",
  "signSignature": "3045022100c13afdac19300d40f34bdaea6886ab2d87b3aa16bcf363b71ea4cb22f6f82e06022005f6fda821a4f95b645ed86e4f3c78fa75b49092e291af95015dc6561f0cdcb3",
  "signature": "304502210098ecc65d1e502cf6a9527e491ca1a88ae349aaf7ec187f58677d9cd004f012bc0220205cb288186eb34a0a552091b7e834ea33d2b7d7d3e03b98c4347227f60bfe45",
  "timestamp": 69408909,
  "type": 0,
  "vendorField": "vendorField value"
}
```

Once signatures and id are set, the transaction is ready to be broadcasted to the blockchain.

<!-- ```python
>>> tx["amount"] = 100000000
>>> tx["vendorField"] = "Smartbridge data"
>>> tx["recipientId"] = "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk"
>>> tx["secret"] = "a 12 word secret passphrase"
>>> # secret is not saved, but keys are stored as private class variables
>>> blockchain.Transaction._publicKey
'020c6f784ccc53d6e280ebca5055a6639415e583c9c637791d0c20166bb9f4bb71'
>>> blockchain.Transaction._privateKey
'ce56d58d9d4d34a773c3a2ed79f23377c771cd687dbcce17b5d53dce89bd2fce'
>>> # tx is also updated with senderPublicKey field
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "020c6f784ccc53d6e280ebca5055a6639415e583c9c637791d0c20166bb9f4bb71",
  "timestamp": 57827307,
  "type": 0,
  "vendorField": "Smartbridge data"
}
```

`asset`, `timestamp` and `type` fields are automatically created. All fields can be initialized using keyword arguments&nbsp;:

```python
>>> blockchain.Transaction(
...    amount=100000000,
...    vendorField="Smartbridge data",
...    secret="a 12 word secret passphrase",
...    recipientId="D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk")
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderPublicKey": "020c6f784ccc53d6e280ebca5055a6639415e583c9c637791d0c20166bb9f4bb71",
  "timestamp": 57827828,
  "type": 0,
  "vendorField": "Smartbridge data"
}
```

### Set transfer fees

Ark blockchain allows two types of fees&nbsp;: `static` and `dynamic`([AIP16](https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-16.md))

```python
>>> tx.useStaticFee()
>>> tx.setFees()
>>> tx["fee"]
10000000
>>> # dynamic fee using avgFee level
>>> tx.useDynamicFee()
>>> tx.setFees()
>>> tx["fee"]
684253
>>> # dynamic fee at minFee level
>>> tx.useDynamicFee("minFee")
>>> tx.setFees()
>>> tx["fee"]
254000
>>> # dynamic fee using a custom fee multiplier
>>> tx.useDynamicFee(10000)
>>> tx.setFees()
>>> tx["fee"]
990000
```

### Sign transfer

Once public and private keys are stored in `Transaction` object, the simplest way to sign a transaction (`senderId` field is automatically added)&nbsp;:
```python
>>> tx.sign()
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "fee": 990000,
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderId": "DC53P3wf42jP5NzExzKzX1YGHv61pbNgVD",
  "senderPublicKey": "020c6f784ccc53d6e280ebca5055a6639415e583c9c637791d0c20166bb9f4bb71",
  "signature": "304402202a8dbf59ce567fe22e8e85d0e4d89fd0c9a8a2d642603d025096ac440ad4746c02205c9517e4e72762531318097e1a89bda6d89f00bd96bd119a1511498057f8ed83",
  "timestamp": 57827307,
  "type": 0,
  "vendorField": "Smartbridge data"
}
```
You may sign with another secret (check `senderPublicKey`, `senderId` and `signature` changes):

```python
>>> tx.signWithSecret("another 12 world secret passphrase")
{
  "amount": 100000000,
  "asset": {},
  "fee": 990000,
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderId": "DBJbxDPiv6x5xjH4mVFPuCCqx57D8dmyuP",
  "senderPublicKey": "021b4f96931a26926864d1bbdfd63e8a932f409b7f0e4a61dab9cab2962e5a1c45",
  "signature": "3044022014cbb98dc9fb2594db28b4e1d8380e990fee4c63ab173640410a279fcfd70d66022074b219cd4264c4c04e0bc07c79d52221f1cf50ea74e2c4f68103186253f5a0d9",
  "timestamp": 57827307,
  "type": 0,
  "vendorField": "Smartbridge data"
}
```

Or if you have your public and private keys&nbsp;:
```python
>>> tx.signWithKeys(
...     '025f81956d5826bad7d30daed2b5c8c98e72046c1ec8323da336445476183fb7ca',
...     '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08')
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "fee": 990000,
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderId": "DM7UiH4b2rW2Nv11Wu6ToiZi8MJhGCEWhP",
  "senderPublicKey": "025f81956d5826bad7d30daed2b5c8c98e72046c1ec8323da336445476183fb7ca",
  "signature": "3045022100fb45b86dc276f0c587387f7ec87b92f50a8b543f5a9ace655c161fa971a3ed8002205e614b67b135264cf29f9fd951678570925b4b41baa9e6461f83ea9d496b26e4",
  "timestamp": 57827307,
  "type": 0,
  "vendorField": "Smartbridge data"
}
```

### Identify transfer

```python
>>> tx.identify()
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "fee": 990000,
  "id": "610e8fe28a3ed219fadb7c142350959c4453f47cf18b45ffaf515e00d1c0f04d",
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderId": "DM7UiH4b2rW2Nv11Wu6ToiZi8MJhGCEWhP",
  "senderPublicKey": "025f81956d5826bad7d30daed2b5c8c98e72046c1ec8323da336445476183fb7ca",
  "signature": "3045022100fb45b86dc276f0c587387f7ec87b92f50a8b543f5a9ace655c161fa971a3ed8002205e614b67b135264cf29f9fd951678570925b4b41baa9e6461f83ea9d496b26e4",
  "timestamp": 57827307,
  "type": 0,
  "vendorField": "Smartbridge data"
}
```

## The finalize function

`finalize` function does thoses 4 steps once transaction is created.

```python
>>> tx = blockchain.Transaction(
...    amount=100000000,
...    vendorField="Smartbridge data",
...    secret="a 12 word secret passphrase",
...    secondSecret="another 12 word secret passphrase",
...    recipientId="D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk")
>>> tx.finalize()
>>> tx
{
  "amount": 100000000,
  "asset": {},
  "fee": 990000,
  "id": "3569eccbcee38c7d49ee87b16cd1268c3028c9d5a0663e34da2d4c968d6fd8c7",
  "recipientId": "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
  "senderId": "DC53P3wf42jP5NzExzKzX1YGHv61pbNgVD",
  "senderPublicKey": "020c6f784ccc53d6e280ebca5055a6639415e583c9c637791d0c20166bb9f4bb71",
  "signSignature": "30440220126e847817234724654516a39c0f515ade437f24ab94873b1bcf131593c4f288022027fb4b683b67f41639bb4802c736c3502940575797ace42ce6aaff7b9cea426c",
  "signature": "3045022100e0fd7f47d624b6357e9bda3ed747bafaeb00e2d014ec4a5cd3bc038e05c26aca02207e262dedd74960e5eedc719b06d83a882543e33ef288634df3dfd587e20bad9a",
  "timestamp": 60646211,
  "type": 0,
  "vendorField": "Smartbridge data"
}
``` -->
