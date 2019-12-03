# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import os
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
    TEMPLATES_AUTO_RELOAD=True
)


def handle_exception(e_type, e_value, e_traceback):
    return flask.redirect(
        json.dumps({
            "error": "%s" % e_type,
            "value": "%s" % e_value,
            "traceback": "%s" % e_traceback
        })
    )
sys.excepthook = handle_exception


def load(publicKey, txid):
    registry = loadJson(
        os.path.join(
            dposlib.ROOT, ".registry", rest.cfg.network, publicKey
        )
    )
    return registry.get(txid, False)


def dump(tx):
    path = os.path.join(
        dposlib.ROOT, ".registry", rest.cfg.network, tx["senderPublicKey"]
    )
    registry = loadJson(path)
    registry[identify(tx)] = tx
    dumpJson(registry, path)


def identify(tx):
    return dposlib.core.crypto.getIdFromBytes(
        dposlib.core.crypto.getBytes(
            tx,
            exclude_sig=True,
            exclude_multi_sig=True,
            exclude_second_sig=True
        )
    )


@app.route("/get/<string:publicKey>", methods=["GET"])
def get(publicKey):
    return json.dumps(
        loadJson(
            os.path.join(
                dposlib.ROOT, ".registry", rest.cfg.network, publicKey
            )
        )
    )


@app.route("/post", methods=["POST"])
def post():

    if flask.request.method == "POST":
        data = json.loads(flask.request.data).get("data", False)

        if not data:
            return {"error": "not a valid transaction"}

        tx = dposlib.core.Tranaction(data)
        dump(tx)

    else:
        return {"error": "POST request only allowed here"}


@app.route("/put/<string:publicKey>/<string:txid>", methods=["PUT"])
def put(publicKey, txid):

    if flask.request.method == "PUT":
        data = json.loads(flask.request.data).get("data", False)

        if not data:
            return {"error": "not a valid signature"}

        tx = load(publicKey, txid)
        if not tx:
            return {"error": "%s not found" % txid}

        tx = dposlib.core.Transaction(tx)
        if tx["type"] == 4:
            index = tx.asset["multiSignature"]["publicKeys"].index(
                publicKey
            )
        elif tx.get("_multisignature", False):
            if publicKey not in tx._multisignature["publicKeys"]:
                return {
                    "error": "public key %s not allowed here" % publicKey
                }
            index = tx._multisignature["publicKeys"].index(publicKey)
        else:
            return {"error": "multisignature not to be used here"}

        check = dposlib.core.crypto.verifySignatureFromBytes(
            dposlib.core.crypto.getBytes(
                tx,
                exclude_sig=True,
                exclude_multi_sig=True,
                exclude_second_sig=True
            ),
            data["publicKey"], data["signature"]
        )
        if check:
            tx["signatures"] = tx.get("signatures", []) + [
                "%02x" % index + data["signature"]
            ]
            if len(tx["signatures"]) >= tx._multisignature["min"]:
                tx.identify()
                return rest.POST.api.transactions(transactions=[tx])
            else:
                return {"success": "signature added to transaction"}
            dump(tx)
        else:
            return {"error": "signature dos not match public key"}

    else:
        return {"error": "PUT request only allowed here"}
