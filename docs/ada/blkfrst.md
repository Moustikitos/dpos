<a id="dposlib.ada"></a>

# dposlib.ada

Cardano specific package trough [`Blockfrost`](https://blockfrost.io) provider.

You have to signup first and create a project. Token can be used on cardano
testnet `shelley` or mainnet `ada` according to your project. `blockfrost` API
can be requested using `rest` module.

```python
>>> from dposlib import rest
>>> rest.use("shelley")
Paste your blockfrost.io token > testnetTQemTkbWv...YceJXT
True
>>> rest.GET.api.v0.blocks.latest()
{
    'time': 1637339033,
    'height': 3086136,
    'hash': '72cd383b6c6c5a1a1027b11da58b637eb60ab1520247da10f1558ce2544cb129',
    'slot': 42969817,
    'epoch': 169,
    'epoch_slot': 331417,
    'slot_leader': 'pool1ta0df6et5d22k2khezze70dvly6kgcm6zp0gpjxc5lwrce0seyq',
    'size': 630,
    'tx_count': 2,
    'output': '49900070463',
    'fees': '339142',
    'block_vrf':
        'vrf_vk1rm9kkh9czf6v2a2qe5ah3jzrh4gr8y04ezsjak79wkspfnn4e73qfdxp5n',
    'previous_block':
        'fa98d456b0be6ac38f86222f3606d122e4b2d9216280fd861c06a3b08caeb078',
    'next_block': None,
    'confirmations': 0,
    'status': 200
}
```

