# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import os
import sys
import json
import flask
import dposlib

from dposlib import rest
from dposlib.util.data import loadJson, dumpJson

# create the application instance
app = flask.Flask("ARK multisig wallet")
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
    #
    # DEBUG=True
)


def load(network, publicKey, txid):
    registry = loadJson(
        os.path.join(dposlib.ROOT, ".registry", network, publicKey)
    )
    return registry.get(txid, False)


def dump(network, tx):
    path = os.path.join(
        dposlib.ROOT, ".registry", network, tx["senderPublicKey"]
    )
    registry = loadJson(path)
    id_ = identify(tx)
    registry[id_] = tx
    dumpJson(registry, path)
    return id_


def identify(tx):
    return dposlib.core.crypto.getIdFromBytes(
        dposlib.core.crypto.getBytes(
            tx,
            exclude_sig=True,
            exclude_multi_sig=True,
            exclude_second_sig=True
        )
    )


@app.errorhandler(Exception)
def handle_exception(error):
    return json.dumps({"python error": "%r" % error}), 500


@app.route("/multisignature/<string:network>", methods=["GET"])
def getAll(network):
    result = {}
    search_path = os.path.join(dposlib.ROOT, ".registry", network)
    if os.path.exists(search_path) and os.path.isdir(search_path):
        for name in os.listdir(search_path):
            result[name] = loadJson(os.path.join(search_path, name))
    return json.dumps({"data": result}), 200


@app.route(
    "/multisignature/<string:network>/<string:publicKey>",
    methods=["GET"]
)
def getWallet(network, publicKey):
    return json.dumps({
        "data": loadJson(
            os.path.join(dposlib.ROOT, ".registry", network, publicKey)
        )
    }), 200


@app.route("/multisignature/<string:network>/post", methods=["POST"])
def postNewTransactions(network):

    if network != getattr(rest.cfg, "network", False):
        rest.use(network)

    if flask.request.method == "POST":
        data = json.loads(flask.request.data)

        if "transactions" not in data:
            return json.dumps({"API error": "transaction(s) not found"})

        transactions = data.get("transactions", [])
        msg = []
        txs = []
        for tx in transactions:
            idx = transactions.index(tx)
            try:
                tx = dposlib.core.Transaction(tx)
                id_ = dump(network, tx)
            except Exception as error:
                msg.append("transaction #%d rejected (%r)" % (idx, error))
            else:
                txs.append(tx)
                msg.append(
                    "transaction #%d successfully posted (id:%s)" % (idx, id_)
                )

        return json.dumps({"messages": msg, "transactions": txs}), 200

    else:
        return json.dumps({"API error": "POST request only allowed here"})


@app.route(
    "/multisignature/<string:network>/put/<string:publicKey>",
    methods=["PUT"]
)
def putSignature(network, publicKey):

    if network != getattr(rest.cfg, "network", False):
        rest.use(network)

    if flask.request.method == "PUT":
        data = json.loads(flask.request.data)

        if "pair" not in data:
            return json.dumps({"error": "no signature found"})

        txid = data["pair"]["id"]
        ms_publicKey = data["pair"]["publicKey"]
        signature = data["pair"]["signature"]
        print(network, publicKey, txid)
        tx = load(network, publicKey, txid)

        if not tx:
            return json.dumps({"API error": "transaction %s not found" % txid})

        tx = dposlib.core.Transaction(tx)
        print(tx._multisignature, ms_publicKey)
        if tx["type"] == 4:
            index = tx.asset["multiSignature"]["publicKeys"].index(
                ms_publicKey
            )
        elif getattr(tx, "_multisignature", False):
            if ms_publicKey not in tx._multisignature["publicKeys"]:
                return json.dumps({
                    "API error": "public key %s not allowed here" % ms_publicKey
                })
            index = tx._multisignature["publicKeys"].index(ms_publicKey)
        else:
            return json.dumps({"error": "multisignature not to be used here"})

        check = dposlib.core.crypto.verifySignatureFromBytes(
            dposlib.core.crypto.getBytes(
                tx,
                exclude_sig=True,
                exclude_multi_sig=True,
                exclude_second_sig=True
            ),
            ms_publicKey, signature
        )
        #
        if check:
            tx["signatures"] = tx.get("signatures", []) + \
                               ["%02x" % index + signature]
            dump(network, tx)
            if len(tx["signatures"]) >= tx._multisignature["min"]:
                tx.identify()
                return json.dumps({
                    "success": "transaction sent to blockchain",
                    "message": rest.POST.api.transactions(transactions=[tx]),
                    "data": tx
                }), 200
            else:
                return json.dumps({
                    "success": "signature added to transaction",
                    "data": tx
                }), 200
        else:
            return json.dumps({
                "API error": "signature does not match owner keys"
            })

    else:
        return json.dumps({"API error": "PUT request only allowed here"})
