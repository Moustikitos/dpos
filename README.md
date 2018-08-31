# `dposlib`

`dposlib` package aims to provide a simple API to link major DPOS blockchain.

**API use:**
```python
>>> from dposlib import rest
>>> rest.use("ark")
>>> rest.GET.api.delegates.get(username="arky")
{'delegate': {'productivity': 98.63, 'approval': 1.05, 'rate': 38, 'producedblocks': 108730, 'username': 'arky', 'missedblocks': 1512, 'vote': '142726557022385', 'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d60a15e9', 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE'}, 'success': True}
```

**Transaction baking:**
```python
>>> from dposlib.blockchain import Transaction
>>> Transaction.link("secret", "secondSecret")
>>> tx = Transaction(amount=0, recipientId="ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE")
>>> tx.sign()
>>> tx.signSign()
>>> tx.identify()
>>> tx
{'signature': '3045022100c34d7f429c4b65f4a45adf4fe69a56dd3cd025de197eb7f1979d804e2e67582d022064a7e0fc8b9b225880e98a7376116d9e72e6fd0d0d74c0106a77b066560f5e2c', 'type': 0, 'signSignature': '3045022100b9f5f8ff3849512c2bb3f37cad88d2bc9ea9945d1df8658bc98d8c5f19b2ce79022011e8bb260e83419cb56c0ac2e34690b96097d9293418eaf39078da02510b237e', 'recipientId': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE', 'senderPublicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933', 'timestamp': 45566065, 'fee': 10000000, 'id': 'f4c6330dcd9a7e79e191641e0c1a48c00fcee62800372333ad06074bba118677', 'amount': 0}
```
