# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import os
import json
import flask
import dposlib
import traceback

from dposlib import rest
from dposlib.util.data import loadJson, dumpJson
from dposlib.ark import crypto
from dposlib.util.bin import hexlify

# create the application instance
app = flask.Flask("ARK multisig server")
app.config.update(
    # 600 seconds = 10 minutes lifetime session
    PERMANENT_SESSION_LIFETIME=300,
    # used to encrypt cookies
    # secret key is generated each time app is restarted
    SECRET_KEY=os.urandom(24),
    # JS can't access cookies
    SESSION_COOKIE_HTTPONLY=True,
    # bi use of https
    SESSION_COOKIE_SECURE=False,
    # update cookies on each request
    # cookie are outdated after PERMANENT_SESSION_LIFETIME seconds of idle
    SESSION_REFRESH_EACH_REQUEST=True,
    # reload templates without server restart
    TEMPLATES_AUTO_RELOAD=True,
)


def load(network, ms_publicKey, txid):
    """
    Load a transaction from a specific registry.

    Args:
        network (:class:`str`): blockchain name
        ms_publicKey (:class:`str`): encoded-compresed public key as hex string
        txid (:class:`str`): transaction id

    Returns:
        :class:`dict`: transaction data
    """
    registry = loadJson(
        os.path.join(dposlib.ROOT, ".registry", network, ms_publicKey)
    )
    return registry.get(txid, False)


def pop(network, tx):
    """
    Remove a transaction from registry. Wallet registry is removed if empty.

    Args:
        network (:class:`str`): blockchain name
        publicKey (:class:`str`): encoded-compresed public key as hex string
    """
    path = os.path.join(
        dposlib.ROOT, ".registry", network, tx["senderPublicKey"]
    )
    registry = loadJson(path)
    tx.pop("id", False)
    registry.pop(identify(tx), False)
    if not(len(registry)):
        os.remove(path)
    else:
        dumpJson(registry, path)


def dump(network, tx):
    """
    Add a transaction into registry. ``senderPublicKey`` field is used to
    create registry if it does not exist.

    Args:
        network (:class:`str`):
            blockchain name
        tx (:class:`dict` or :class:`dposlib.blockchain.Transaction`):
            transaction to store
    """
    path = os.path.join(
        dposlib.ROOT, ".registry", network, tx["senderPublicKey"]
    )
    registry = loadJson(path)
    tx.pop("id", False)
    id_ = identify(tx)
    registry[id_] = tx
    dumpJson(registry, path)
    return id_


def identify(tx):
    """
    Identify a transaction.

    Args:
        tx (:class:`dict` or :class:`dposlib.blockchain.Transaction`):
            transaction to identify
    Returns:
        :class:`str`: transaction id used by registries
    """
    return crypto.getIdFromBytes(
        crypto.getBytes(
            tx,
            exclude_sig=True,
            exclude_multi_sig=True,
            exclude_second_sig=True
        )
    )


def append(network, *transactions):
    response = {}
    for tx in transactions:
        idx = transactions.index(tx) + 1
        try:
            if not isinstance(tx, dposlib.core.Transaction):
                tx = dposlib.core.Transaction(tx)
            signatures = tx.get("signatures", [])
            if len(signatures) == 0:
                response["errors"] = response.get("errors", []) + [
                    "transaction #%d rejected (one signature is mandatory)"
                    % idx
                ]
            else:
                checks = []
                serialized = crypto.getBytes(tx, exclude_multi_sig=True)
                for sig in signatures:
                    pk_idx, sig = int(sig[0:2], 16), sig[2:]
                    checks.append(crypto.verifySignatureFromBytes(
                        serialized, tx._multisignature["publicKeys"][pk_idx],
                        sig
                    ))
                if False in checks:
                    response["errors"] = response.get("errors", []) + [
                        "transaction #%d rejected (bad signature)"
                        % idx
                    ]
                else:
                    id_ = dump(network, tx)
                    response["success"] = response.get("success", []) + [
                        "transaction #%d successfully posted" % (idx)
                    ]
                    response["ids"] = response.get("ids", []) + [id_]
        except Exception as error:
            response["errors"] = response.get("errors", []) + [
                "transaction #%d rejected (%r)" % (idx, error)
            ]
        # else:
        #     response["success"] = response.get("success", []) + [
        #         "transaction #%d successfully posted" % (idx)
        #     ]
        #     response["ids"] = response.get("ids", []) + [id_]
    return json.dumps(response), 201


def broadcast(network, tx):
    tx["id"] = crypto.getId(tx)
    response = rest.POST.api.transactions(transactions=[tx])
    if len(response.get("data", {}).get("broadcast", [])):
        code = 200
        pop(network, tx)
    else:
        code = 202
        dump(network, tx)
    return json.dumps(response), code


@app.after_request
def apply_caching(response):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    tl = traceback.format_exc().splitlines()
    return json.dumps({"python error": [tl[0], tl[-1]]})


@app.route("/multisignature/<string:network>", methods=["GET"])
def getAll(network):
    """
    ``GET /multisignature/{network}`` endpoint. Return all public keys issuing
    multisignature transactions.

    Args:
        network (:class:`str`): blockchain network name
    Returns:
        :class:`dict`: all registries
    """
    result = {}
    search_path = os.path.join(dposlib.ROOT, ".registry", network)
    if os.path.exists(search_path) and os.path.isdir(search_path):
        for name in os.listdir(search_path):
            result[name] = loadJson(os.path.join(search_path, name))
        return json.dumps({"success": True, "data": result}), 200
    else:
        return json.dumps({"success": False})


@app.route(
    "/multisignature/<string:network>/<string:ms_publicKey>", methods=["GET"]
)
def getWallet(network, ms_publicKey):
    """
    ``GET /multisignature/{network}/{ms_publicKey}`` endpoint. Return all
    pending transactions issued by a specific public key.
    """
    if flask.request.method != "GET":
        return json.dumps({
            "success": False,
            "API error": "GET request only allowed here"
        })

    wallet = loadJson(
        os.path.join(dposlib.ROOT, ".registry", network, ms_publicKey)
    )
    if len(wallet):
        return json.dumps({"success": True, "data": wallet}), 200
    else:
        return json.dumps({"success": False})


@app.route(
    "/multisignature/<string:network>/<string:ms_publicKey>/<string:txid>",
    methods=["GET"]
)
def getTransaction(network, ms_publicKey, txid):
    """
    ``GET /multisignature/{network}/{ms_publicKey}/{txid}`` endpoint. Return
    specific pending transaction from a specific public key.
    """
    if flask.request.method != "GET":
        return json.dumps({
            "success": False,
            "API error": "GET request only allowed here"
        })

    tx = load(network, ms_publicKey, txid)
    if tx:
        return json.dumps({"success": True, "data": tx}), 200
    else:
        return json.dumps({"success": False})


@app.route(
    "/multisignature/<string:network>/<string:ms_publicKey>"
    "/<string:txid>/serial", methods=["GET"]
)
def getSerial(network, ms_publicKey, txid):
    """
    ``GET /multisignature/{network}/{ms_publicKey}/{txid}/serial`` endpoint.
    Return specific pending transaction serial from a specific public key.
    """
    if network != getattr(rest.cfg, "network", False):
        rest.use(network)

    if flask.request.method != "GET":
        return json.dumps({
            "success": False,
            "API error": "GET request only allowed here"
        })

    tx = load(network, ms_publicKey, txid)
    if tx:
        return json.dumps({
            "success": True,
            "data": hexlify(crypto.getBytes(tx))
        }), 200
    else:
        return json.dumps({"success": False})


@app.route("/multisignature/<string:network>/create", methods=["POST"])
def registerWallet(network):
    """
    ``POST /multisignature/{network}/create`` endpoint. Register as
    multisignature wallet::

        data = {
            "info": {
                "senderPublicKey": wallet_public_key_issuing_transaction,
                "min": minimum_signature_required,
                "publicKeys": public_key_list
            }
        }

    Once created on server, registration transaction have to be remotly signed.
    See :func:`putSignature`.
    """

    if network != getattr(rest.cfg, "network", False):
        rest.use(network)

    if flask.request.method == "POST":
        data = json.loads(flask.request.data)

        if "info" not in data:
            return json.dumps({"error": "no info"})

        tx = dposlib.core.registerMultiSignature(
            data["info"]["min"], *data["info"]["publicKeys"]
        )
        tx.senderPublicKey = data["info"]["senderPublicKey"]
        tx.useDynamicFee(data["info"].get("fee", "avgFee"))
        tx.setFee()

        return append(network, tx)

    else:
        return json.dumps({
            "success": False,
            "API error": "POST request only allowed here"
        })


@app.route("/multisignature/<string:network>/post", methods=["POST"])
def postNewTransactions(network):
    """
    ``POST /multisignature/{network}/post`` endpoint. Post transaction
    from multisignature wallet to be remotly signed::

        data = {"transactions": [tx1, tx2, ... txi ..., txn]}

    See :func:`putSignature`.
    """
    if network != getattr(rest.cfg, "network", False):
        rest.use(network)

    if flask.request.method == "POST":
        data = json.loads(flask.request.data)

        if "transactions" not in data:
            return json.dumps({"API error": "transaction(s) not found"})

        return append(network, *data.get("transactions", []))

    else:
        return json.dumps({
            "success": False,
            "API error": "POST request only allowed here"
        })


@app.route(
    "/multisignature/<string:network>/<string:ms_publicKey>/put",
    methods=["PUT"]
)
def putSignature(network, ms_publicKey):
    """
    ``PUT /multisignature/{network}/{ms_publicKey}/put`` endpoint. Add
    signature to a pending transaction::

        data = {
            "info": {
                "id": pending_transaction_id,
                "signature": signature,
                "publicKey": associated_public_key
            } [ + {
                "fee": optional_fee_value_to_use
            } ]
        }
    """
    if network != getattr(rest.cfg, "network", False):
        rest.use(network)

    if flask.request.method == "PUT":
        data = json.loads(flask.request.data)

        if "info" not in data:
            return json.dumps({"error": "no info"})

        txid = data["info"]["id"]
        tx = load(network, ms_publicKey, txid)

        if not tx:
            return json.dumps({
                "success": False,
                "API error": "transaction %s not found" % txid
            })

        tx = dposlib.core.Transaction(tx)
        publicKey = data["info"]["publicKey"]
        signature = data["info"]["signature"]

        # sign type 4
        if tx.type == 4 and publicKey == tx.senderPublicKey:
            publicKeys = tx["asset"]["multiSignature"]["publicKeys"]
            # type 4 signatures field is full
            if len(tx.get("signatures", [])) == len(publicKeys):
                # and signature matches type 4 issuer's public key
                if crypto.verifySignatureFromBytes(
                    crypto.getBytes(tx), publicKey, signature
                ):
                    tx.signature = signature
                    dump(network, tx)
                    if tx._secondPublicKey is None:
                        # if no need to signSign --> broadcast tx and return
                        # network response
                        return broadcast(network, tx)
                    else:
                        return json.dumps({
                            "success": True,
                            "message": "issuer signature added"
                        })
                else:
                    return json.dumps({
                        "success": False,
                        "API error": "signature does not match issuer key"
                    })
            else:
                return json.dumps({
                    "success": False,
                    "API error": "one or more signature missing"
                })

        # signSign
        if publicKey == tx._secondPublicKey:
            # if tx already signed by issuer
            if "signature" in tx:
                # and signature matches type 4 issuer 's second public key
                if crypto.verifySignatureFromBytes(
                    crypto.getBytes(tx), publicKey, signature
                ):
                    # signSign, broadcast and return network response
                    tx.signSignature = signature
                    return broadcast(network, tx)
                else:
                    return json.dumps({
                        "success": False,
                        "API error": "signature does not match issuer "
                                     "second key"
                    })
            else:
                return json.dumps({
                    "success": False,
                    "API error": "transaction have to be signed first"
                })

        # multi owner signature
        try:
            # try to get public key index
            if tx["type"] == 4:
                index = \
                    tx.asset["multiSignature"]["publicKeys"].index(publicKey)
            else:
                index = tx._multisignature["publicKeys"].index(publicKey)
        except ValueError:  # retuned by [].index if not found
            return json.dumps({
                "success": False,
                "API error": "public key %s not allowed here" % publicKey
            })
        except (KeyError, AttributeError):
            return json.dumps({
                "success": False,
                "API error": "multisignature not to be used here"
            })
        # verify signature
        check = crypto.verifySignatureFromBytes(
            crypto.getBytes(
                tx, exclude_sig=True, exclude_multi_sig=True,
                exclude_second_sig=True
            ), publicKey, signature
        )
        # if signature matches
        if check:
            # set is used here to remove doubles
            tx["signatures"] = list(
                set(tx.get("signatures", []) + ["%02x" % index + signature])
            )
            if tx["type"] != 4 and \
               len(tx.get("signatures", [])) >= tx._multisignature["min"]:
                return broadcast(network, tx)
            else:
                dump(network, tx)
                return json.dumps({
                    "success": True,
                    "message": "signature added to transaction",
                }), 201
        else:
            return json.dumps({
                "success": False,
                "API error": "signature does not match owner keys"
            })

    else:
        return json.dumps({
            "success": False,
            "API error": "PUT request only allowed here"
        })
