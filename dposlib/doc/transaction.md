# class `Transaction`

`Transaction` object is at the center of `dposlib` package. It is a python dictionary containing basic functions to interact with a blockchain environement. `Transaction` class is available in `blockchain` sub package.

A blockchain must be loaded first&nbsp;:

```python
>>> from dposlib import blockchain
>>> from dposlib import rest
>>> rest.use("dark")
```

### Create a transfer transaction

```python
>>> tx = blockchain.Transaction()
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
```
