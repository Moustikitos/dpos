<a id="dposlib.ark"></a>

# dposlib.ark

ARK.io specific package.

See [Ark API documentation](
    https://api.ark.dev/public-rest-api/getting-started
) to see how to use http calls.

```python
>>> import dposlib
>>> from dposlib import rest
>>> rest.use("ark")
True
>>> # reach http://api.ark.io/api/delegates/arky endpoint using GET
>>> # HTTP request builder
>>> rest.GET.api.delegates.arky()["username"]
'arky'
>>> dlgt = dposlib.core.api.Delegate("arky")
>>> dlgt.forged
{u'rewards': 397594.0, u'total': 401908.71166083, u'fees': 4314.71166083}
>>> dposlib.core.crypto.getKeys("secret")["publicKey"]
'03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933'
>>> dposlib.core.transfer(
...     1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
...     u"\u2728 simple transfer vendorField"
... )
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 0,
  "vendorField": "\u2728 simple transfer vendorField",
  "version": 1
}
>>> dposlib.core.htlcLock(
...     1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
...     "my secret lock", expiration=12,
...     vendorField=u"\u2728 simple htlcLock vendorField"
... )
{
  "amount": 100000000,
  "asset": {
    "lock": {
      "secretHash":
        "dbaed2f2747c7aa5a834b082ccb2b648648758a98d1a415b2ed9a22fd29d47cb",
      "expiration": {
        "type": 1,
        "value": 82567745
      }
    }
  },
  "network": 23,
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 8,
  "typeGroup": 1,
  "vendorField": "\u2728 simple htlcLock vendorField",
  "version": 2
}
```

<a id="dposlib.ark.init"></a>

#### init

```python
def init(seed=None)
```

Blockchain initialisation. It stores root values in `cfg` module.

<a id="dposlib.ark.stop"></a>

#### stop

```python
def stop()
```

Stop daemon initialized by `init` call.

