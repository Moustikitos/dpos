<a id="dposlib.ark.api"></a>

# dposlib.ark.api

<a id="dposlib.ark.api.isLinked"></a>

#### isLinked

```python
def isLinked(func)
```

`Python decorator`.
First argument of decorated function have to be a
[`dposlib.ark.api.Content`](api.md#dposlib.ark.api.Content)
or an object containing a valid `address`, `_derivationPath` or `publicKey`
attribute. It executes the decorated `function` if the object is correctly
linked using `dposlib.ark.api.link` definition.

<a id="dposlib.ark.api.link"></a>

#### link

```python
def link(cls, secret=None, secondSecret=None)
```

Associates crypto keys into a [`dposlib.ark.api.Content`](
api.md#dposlib.ark.api.Content
) object according to secrets. If `secret` or `secondSecret` are not `str`,
they are considered as `None`. In this case secrets will be asked and
checked from console untill success or `Ctrl+c` keyboard interruption.

**Arguments**:

- `cls` _Content_ - content object.
- `secret` _str_ - secret string. Default set to `None`.
- `secondSecret` _str_ - second secret string. Default set to `None`.
  

**Returns**:

- `bool` - True if secret and second secret match.

<a id="dposlib.ark.api.unlink"></a>

#### unlink

```python
def unlink(cls)
```

Remove crypto keys association.

<a id="dposlib.ark.api.JSDict"></a>

## JSDict Objects

```python
class JSDict(dict)
```

Read only dictionary with js object behaviour.

```python
>>> jsdic = dposlib.ark.JSDict(value=5)
>>> jsdic
{'value': 5}
>>> jsdic.value
5
```

<a id="dposlib.ark.api.Content"></a>

## Content Objects

```python
class Content(object)
```

Live object connected to blockchain. It is initialized with
[`dposlib.rest.GET`](../rest.md#dposlib.rest.GET) request. Object is
updated every 30s. Endpoint response can be a `dict` or a `list`. If it is
a `list`, it is stored in `data` attribute else all fields are stored as
instance attribute.

```python
>>> txs = dposlib.ark.Content(rest.GET.api.transactions)
>>> txs.data[0]["timestamp"]
{
    'epoch': 121912776,
    'unix': 1612013976,
    'human': '2021-01-30T13:39:36.000Z'
}
>>> tx = dposlib.ark.Content(
    rest.GET.api.transactions,
    "d36a164a54df9d1c7889521ece15318d6945e9971fecd0a96a9c18e74e0adbf9",
)
>>> tx.timestamp
{
    'epoch': 121919704,
    'unix': 1612020904,
    'human': '2021-01-30T15:35:04.000Z'
}
>>> tx.amount
212963052
>>> tx.datetime
datetime.datetime(2021, 1, 30, 15, 35, 4, tzinfo=<UTC>)
```

<a id="dposlib.ark.api.Content.__init__"></a>

#### \_\_init\_\_

```python
def __init__(ndpt, *args, **kwargs)
```

**Arguments**:

- `ndpt` _usrv.req.Endpoint_ - endpoint class to be called.
- `*args` - Variable length argument list used by `usrv.req.Endpoint`.
  
  **Kwargs**:
  
  * `keep_alive` *bool* - set hook to update data from blockcahin.
  Default to True.

<a id="dposlib.ark.api.Content.filter"></a>

#### filter

```python
def filter(data)
```

Convert data as JSDict object converting string values in int if
possible.

<a id="dposlib.ark.api.Wallet"></a>

## Wallet Objects

```python
class Wallet(Content)
```

Wallet root class that implements basic wallet behaviour.

<a id="dposlib.ark.api.Wallet.delegate"></a>

#### delegate

Delegate attributes if wallet is registered as delegate.

<a id="dposlib.ark.api.Wallet.username"></a>

#### username

Delegate username if wallet is registered as delegate.

<a id="dposlib.ark.api.Wallet.secondPublicKey"></a>

#### secondPublicKey

Second public key if second signature is set to wallet.

<a id="dposlib.ark.api.Wallet.__init__"></a>

#### \_\_init\_\_

```python
def __init__(address, **kw)
```

**Arguments**:

- `address` _str_ - wallet address or delegate username.
- `**kwargs` - Variable key argument used by
  [`dposlib.ark.api.Content`](api.md#dposlib.ark.api.Content).
  
  **Specific kwargs**:
  
  * `keep_alive` *bool* - automatic update data from blockcahin. Default
  to True.
  * `fee` *int or str* - set fee level as fee multiplier string value or
  one of **minFee**, **avgFee**, **maxFee**. Default to **avgFee**.
  * `fee_included` *bool* - set to True if amout + fee is the total
  desired out flow. Default to False.

<a id="dposlib.ark.api.Wallet.link"></a>

#### link

```python
def link(*args, **kwargs)
```

See [`dposlib.ark.api.link`](api.md#dposlib.ark.api.link).

<a id="dposlib.ark.api.Wallet.unlink"></a>

#### unlink

```python
def unlink()
```

See [`dposlib.ark.api.unlink`](api.md#dposlib.ark.api.unlink).

<a id="dposlib.ark.api.Wallet.send"></a>

#### send

```python
@isLinked
def send(amount, address, vendorField=None, expiration=0)
```

Broadcast a transfer transaction to the ledger.
See [`dposlib.ark.builders.v2.transfer`](
    builders/v2.md#dposlib.ark.builders.v2.transfer
).

<a id="dposlib.ark.api.Wallet.setSecondSecret"></a>

#### setSecondSecret

```python
@isLinked
def setSecondSecret(secondSecret)
```

Broadcast a second secret registration transaction to the ledger.
See [`dposlib.ark.builders.v2.registerSecondSecret`](
    builders/v2.md#dposlib.ark.builders.v2.registerSecondSecret
).

<a id="dposlib.ark.api.Wallet.setSecondPublicKey"></a>

#### setSecondPublicKey

```python
@isLinked
def setSecondPublicKey(secondPublicKey)
```

Broadcast a second secret registration transaction into the ledger.
See [`dposlib.ark.builders.v2.registerSecondPublicKey`](
    builders/v2.md#dposlib.ark.builders.v2.registerSecondPublicKey
).

<a id="dposlib.ark.api.Wallet.setDelegate"></a>

#### setDelegate

```python
@isLinked
def setDelegate(username)
```

Broadcast a delegate registration transaction to the ledger.
See [`dposlib.ark.builders.v2.registerAsDelegate`](
    builders/v2.md#dposlib.ark.builders.v2.registerAsDelegate
).

<a id="dposlib.ark.api.Wallet.upVote"></a>

#### upVote

```python
@isLinked
def upVote(*usernames)
```

Broadcast an up-vote transaction to the ledger.
See [`dposlib.ark.builders.v2.switchVote`](
    builders/v2.md#dposlib.ark.builders.v2.switchVote
).

<a id="dposlib.ark.api.Wallet.downVote"></a>

#### downVote

```python
@isLinked
def downVote(*usernames)
```

Broadcast a down-vote transaction to the ledger.
See [`dposlib.ark.builders.v2.downVote`](
    builders/v2.md#dposlib.ark.builders.v2.downVote
).

<a id="dposlib.ark.api.Wallet.sendIpfs"></a>

#### sendIpfs

```python
@isLinked
def sendIpfs(ipfs)
```

See [`dposlib.ark.builders.v2.registerIpfs`](
    builders/v2.md#dposlib.ark.builders.v2.registerIpfs
).

<a id="dposlib.ark.api.Wallet.multiSend"></a>

#### multiSend

```python
@isLinked
def multiSend(*pairs, **kwargs)
```

See [`dposlib.ark.builder.multiPayment`](
    builders/v2.md#dposlib.ark.builders.v2.multiPayment
).

<a id="dposlib.ark.api.Wallet.resignate"></a>

#### resignate

```python
@isLinked
def resignate()
```

See [`dposlib.ark.builders.v2.delegateResignation`](
    builders/v2.md#dposlib.ark.builders.v2.delegateResignation
).

<a id="dposlib.ark.api.Wallet.sendHtlc"></a>

#### sendHtlc

```python
@isLinked
def sendHtlc(amount, address, secret, expiration=24, vendorField=None)
```

See [`dposlib.ark.builders.v2.htlcLock`](
    builders/v2.md#dposlib.ark.builders.v2.htlcLock
).

<a id="dposlib.ark.api.Wallet.claimHtlc"></a>

#### claimHtlc

```python
@isLinked
def claimHtlc(txid, secret)
```

See [`dposlib.ark.builders.v2.htlcClaim`](
    builders/v2.md#dposlib.ark.builders.v2.htlcClaim
).

<a id="dposlib.ark.api.Wallet.refundHtlc"></a>

#### refundHtlc

```python
@isLinked
def refundHtlc(txid)
```

See [`dposlib.ark.builders.v2.htlcRefund`](
    builders/v2.md#dposlib.ark.builders.v2.htlcRefund
).

<a id="dposlib.ark.api.Wallet.createEntity"></a>

#### createEntity

```python
@isLinked
def createEntity(name, type="business", subtype=0, ipfsData=None)
```

See [`dposlib.ark.builders.v2.entityRegister`](
    builders/v2.md#dposlib.ark.builders.v2.entityRegister
).

<a id="dposlib.ark.api.Wallet.updateEntity"></a>

#### updateEntity

```python
@isLinked
def updateEntity(registrationId, ipfsData, name=None)
```

See [`dposlib.ark.builders.v2.entityUpdate`](
    builders/v2.md#dposlib.ark.builders.v2.entityUpdate
).

<a id="dposlib.ark.api.Wallet.resignEntity"></a>

#### resignEntity

```python
@isLinked
def resignEntity(registrationId)
```

See [`dposlib.ark.builders.v2.entityResign`](
    builders/v2.md#dposlib.ark.builders.v2.entityResign
).

<a id="dposlib.ark.api.Ledger"></a>

## Ledger Objects

```python
class Ledger(Wallet)
```

Ledger wallet api.

<a id="dposlib.ark.api.Webhook"></a>

## Webhook Objects

```python
class Webhook(Content)
```

```python
>>> import dposlib
>>> peer = "http:/127.0.0.1:4004"
>>> target = "http://127.0.0.1/targetted/endpoint"
>>> wh = dposlib.core.api.Webhook(
...   peer, "transaction.applied", target, "amount<1"
... )
security token: 9f86d081884c7d659a2feaa0c55ad015...2b0b822cd15d6c15b0f00a08
>>> dposlib.core.api.webhook.verify("9f86d081884c7d659a2feaa0c55ad015")
True
>>> wh.delete()
{"sucess": True, "status": 204}
```

<a id="dposlib.ark.api.Webhook.condition"></a>

#### condition

```python
@staticmethod
def condition(expr)
```

Webhook condition builder from `str` expression. It is internally used
by [`Webhook.create`](api.md#dposlib.ark.api.Webhook.create) method.

<style>td,th{border:none!important;text-align:left;}</style>
webhook                   | dposlib
------------------------- | ------------
`lt` / `lte`              | `<` / `<=`
`gt` / `gte`              | `>` / `>=`
`eq` / `ne`               | `==` / `!=`
`truthy` / `falsy`        | `?` / `!?`
`regexp` / `contains`     | `\\` / `$`
`between` / `not-between` | `<>` / `!<>`


```python
>>> import dposlib.ark.api as api
>>> api.Webhook.condition("vendorField\\^.*payroll.*$")
{'value': '^.*payroll.*$', 'key': 'vendorField', 'condition': 'regexp'}
>>> api.Webhook.condition("amount<>2000000000000:4000000000000")
{
    'value': {'min': '2000000000000', 'max': '4000000000000'},
    'condition': 'between',
    'key': 'amount'
}
```

**Arguments**:

- `expr` _str_ - human readable expression.
  

**Returns**:

- `dict` - webhook conditions

