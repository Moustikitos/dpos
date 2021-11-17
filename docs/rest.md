<a id="dposlib.rest"></a>

# dposlib.rest

`rest` module provides network loaders and [`usrv.req.EndPoint`](
    https://github.com/Moustikitos/micro-server/blob/master/usrv/req.py#L33
) root class to implement `GET`, `POST`, `PUT` and `DELETE` HTTP requests.

When a specific blockchain package is loaded through `rest.use` definition, a
`dposlib.core` module is available to provide necessary classes and
definitions.

<a id="dposlib.rest.GET"></a>

#### GET

HTTP GET request builder

<a id="dposlib.rest.POST"></a>

#### POST

HTTP POST request builder

<a id="dposlib.rest.PUT"></a>

#### PUT

HTTP PUT request builder

<a id="dposlib.rest.DELETE"></a>

#### DELETE

HTTP DELETE request builder

<a id="dposlib.rest.load"></a>

#### load

```python
def load(name)
```

Load a given blockchain package as `dposlib.core` module. A valid
blockchain package must provide `init(peer=None)` and `stop()` definitions.
Available blockchains are referenced in `dposli.net` module.

**Arguments**:

- `name` _str_ - package name to load.
  

**Raises**:

- `Exception` - if package name is not found or if package can not be
  initialized properly.

<a id="dposlib.rest.use"></a>

#### use

```python
def use(network, **kwargs)
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

