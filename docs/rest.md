<a name="dposlib.rest"></a>
# dposlib.rest

`rest` module provides network loaders and [`usrv.req.EndPoint`](
    https://github.com/Moustikitos/micro-server/blob/master/usrv/req.py#L33
) root class to implement `GET`, `POST`, `PUT` and `DELETE` HTTP requests. See
[Ark API documentation](
    https://api.ark.dev/public-rest-api/getting-started
) to see how to use http calls.

```python
>>> from dposlib import rest
>>> rest.use("ark")
True
>>> # reach http://api.ark.io/api/delegates/arky endpoint using GET
>>> # HTTP request builder
>>> rest.GET.api.delegates.arky()["username"]
'arky'
```

**`core` module**

When `ark` blockchain package is loaded, a `core` module containing transaction
builders, cryptographic and network interface is available.

```python
>>> import dposlib
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

<a name="dposlib.rest.GET"></a>
#### GET

HTTP GET request builder

<a name="dposlib.rest.POST"></a>
#### POST

HTTP POST request builder

<a name="dposlib.rest.PUT"></a>
#### PUT

HTTP PUT request builder

<a name="dposlib.rest.DELETE"></a>
#### DELETE

HTTP DELETE request builder

<a name="dposlib.rest.load"></a>
#### load

```python
load(name)
```

Load a given blockchain package as `dposlib.core` module. A valid
blockchain package must provide `init(peer=None)` and `stop()` definitions.
Available blockchains are referenced in `dposli.net` module.

**Arguments**:

- `name` _str_ - package name to load.
  

**Raises**:

- `Exception` - if package name is not found or if package can not be
  initialized properly.

<a name="dposlib.rest.use"></a>
#### use

```python
use(network, **kwargs)
```

Sets the blockchain parameters in the `dposlib.rest.cfg` module and
initializes blockchain package. Network options can be created or overriden
using `**kwargs` argument.

**Arguments**:

- `network` _str_ - network to initialize.
- `**kwargs` - parameters to be overriden.
  

**Returns**:

- `bool` - True if network connection established, False otherwise.
  

**Raises**:

- `Exception` - if blockchain not defined or if initialization failed.

