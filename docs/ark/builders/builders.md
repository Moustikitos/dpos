<a id="dposlib.ark.builders"></a>

# dposlib.ark.builders

[`dposlib.ark.builders`](builders.md#dposlib.ark.builders) package
provides[`dposlib.ark.tx.Transaction`](../tx.md#dposlib.ark.tx.Transaction)
class and its associated builders. Builders are automatically set into
`dposlib.core` package according to network.

```python
>>> import dposlib
>>> from dposlib import rest
>>> rest.use("dark")
True
>>> tx = dposlib.core.transfer(
...   1,
...   "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
...   u"simple message with sparkle \u2728",
...   version=2
... )
>>> tx.finalize("first secret", "second secret")
>>> broadcastTransactions(tx).get("data", {}).get("broadcast", [])
[u'041ad1e3dd06d29ef59b2c7e19fea4ced0e7fcf9fdc22edcf26e5cc016e10f38']
```

__Available builders according to network__


blockchain|builders
-|-
`*`|transfer, registerSecondSecret, registerSecondPublicKey, 
   |registerAsDelegate, upVote, downVote, registerMultiSignature, registerIpfs
   |delegateResignation, htlcSecret, htlcLock, htlcClaim, htlcRefund,
   |switchVote
`ark`, `dark`|entityRegister, entityUpdate, entityResign
`sxp`, `tsxp`|burn
`nos`, `dnos`|TODO

