[![Downloads](https://pepy.tech/badge/dposlib/week)](https://pepy.tech/project/dposlib)
[![PyPI version shields.io](https://img.shields.io/pypi/v/dposlib.svg)](https://pypi.python.org/pypi/dposlib)
[![GitHub release](https://img.shields.io/github/tag/Moustikitos/dpos.svg)](https://GitHub.com/Moustikitos/dpos/tags)

> `dposlib` package aims to provide a simple API to any blockchain.

## Human writable HTTP Requests

```python
>>> from dposlib import rest
>>> # ~ https://api.ark.io/api/delegates
>>> rest.GET.api.delegates(peer="https://api.ark.io")["data"][0]
{'username': 'dev51', 'address': 'AWBW9QD53oArEEEb965KiRxTXDPKv2iWn8', 'publicKey': '020cafa960cd435d271f4207f1a89900de32ba678a0fbb05455f82cbaf22bce3a5', 'votes': '357110265571266', 'rank': 1, 'isResigned': False, 'blocks': {'produced': 98085, 'last': {'id': 'cca9b41abe637efebe22c49f944f84e92734ee17d6cca457200cb2a37dfef17d', 'height': 18229073, 'timestamp': {'epoch': 147083032, 'unix': 1637184232, 'human': '2021-11-17T21:23:52.000Z'}}}, 'production': {'approval': 2.86}, 'forged': {'fees': '49196332406', 'rewards': '19617000000000', 'total': '19666196332406'}}
>>> # ~ https://service.lisk.com/api/v2/accounts
>>> rest.GET.api.v2.accounts(peer="https://service.lisk.com")["data"][0]
{'summary': {'address': 'lskbwvtd6sp5f5tpvfnu2v3tuvqbwyyfqqeadcawb', 'legacyAddress': '3645487307206542645L', 'balance': '1893122255345680', 'username': '', 'publicKey': '454a1a25a1b603d56a9e924f68238617be00042519fa9ec16f660bc6a13baa78', 'isMigrated': True, 'isDelegate': False, 'isMultisignature': False}, 'knowledge': {'owner': 'Binance', 'description': 'Cold Wallet'}, 'token': {'balance': '1893122255345680'}, 'sequence': {'nonce': '0'}, 'keys': {'numberOfSignatures': 0, 'mandatoryKeys': [], 'optionalKeys': []}, 'dpos': {'delegate': {'username': '', 'consecutiveMissedBlocks': 0, 'lastForgedHeight': 16270293, 'isBanned': False, 'totalVotesReceived': '0'}}}
>>> # ~ https://blockchain.info/tobtc?currency=USD&value=500
>>> rest.GET.tobtc(peer="https://blockchain.info", currency="USD", value="500")
0.00835083
```
