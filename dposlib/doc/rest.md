# `rest` module

This module loads external parameters from `*.net` file and merges blockchain specific ones into the `blockchain.cfg` module.

```python
>>> from dposlib import rest
>>> from dposlib import blockchain
>>> rest.use("dark")
>>> blockchain.cfg.begintime
datetime.datetime(2017, 3, 21, 13, 0, tzinfo=<UTC>)
>>> blockchain.cfg.headers
{'version': '30', 'API-Version': '2', 'Content-Type': 'application/json; charset=utf-8', 'nethash': '2a44f340d76ffc3df204c5f38cd355b7496c9065a1ade2ef92071436bd72e867'}
```

When `rest.use` successfully called, `rest` module provides RESTFULL interface with blockchain. GET, POST, DELETE objects maps any REST url from a pythonic-callable-path object and returns the json response as python dictionary.

```python
>>> # https://dexplorer.ark.io:8443/api/v1/delegates/get?username=darktoons
>>> rest.GET.api.v1.delegates.get(username="darktoons")
{'delegate': {'rate': 42, 'missedblocks': 1342, 'vote': '4774481369341', 'username': 'darktoons', 'address': 'D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk', 'approval': 0.04, 'publicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933', 'producedblocks': 9061, 'productivity': 87.1}, 'success': True}
>>> # https://dexplorer.ark.io:8443/api/v2/delegates/darktoons
>>> rest.GET.api.v2.delegates.darktoons()
{'data': {'blocks': {'missed': 1324, 'last': {'timestamp': {'unix': 1547903162, 'epoch': 57801962, 'human': '2019-01-19T13:06:02.000Z'}, 'height': 1258744, 'id': '12164145821698517518'}, 'produced': 9060}, 'username': 'darktoons', 'address': 'D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk', 'forged': {'fees': 8826761584, 'total': 1820826761584, 'rewards': 1812000000000}, 'votes': 4774281369341, 'publicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933', 'production': {'approval': 0.04, 'productivity': 87.25}, 'rank': 42}}
```
