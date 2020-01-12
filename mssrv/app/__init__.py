# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import os
import sys
import json
import flask

import dposlib

from functools import wraps
from dposlib import rest, net
from dposlib.util.data import loadJson, dumpJson
from mssrv import identify, client


# create the application instance
app = flask.Flask("ARK multisig site")
app.config.update(
    # 600 seconds = 10 minutes lifetime session
    PERMANENT_SESSION_LIFETIME=300,
    # used to encrypt cookies
    # secret key is generated each time app is restarted
    SECRET_KEY=os.urandom(24),
    # JS can't access cookies
    SESSION_COOKIE_HTTPONLY=True,
    # cookie stored only if use of https
    SESSION_COOKIE_SECURE=True,
    # update cookies on each request
    # cookie are outdated after PERMANENT_SESSION_LIFETIME seconds of idle
    SESSION_REFRESH_EACH_REQUEST=True,
    # reload templates without server restart
    TEMPLATES_AUTO_RELOAD=True,
)

app.root_path = __path__[0]
SYNCH_FOLDER = os.path.join(app.root_path, ".synch")


########################
# css reload bugfix... #
########################
def _url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get("filename", False)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            try:
                values["q"] = int(os.stat(file_path).st_mtime)
            except OSError:
                pass
    return flask.url_for(endpoint, **values)
########################


def _link_peer(peer="http://127.0.0.1:5000"):
    client.API_PEER = app.peer = peer


def _fix_tx(t):
    for key in ["amount", "fee", "nonce"]:
        t[key] = int(t[key])
    return t


def _ark_srv_synch():
    data = {}
    if not hasattr(rest.cfg, "pubkeyHash"):
        return
    path = os.path.join(SYNCH_FOLDER, "data.%d" % rest.cfg.pubkeyHash)
    try:
        for server in loadJson(
            os.path.join(__path__[0], "server.json")
        ):
            req = rest.GET.transactions(peer=server)
            if req:
                pendings = [
                    _fix_tx(elem["data"])
                    for elem in req
                    if elem["data"]["network"] == rest.cfg.pubkeyHash
                ]
                data.update(
                    dict(
                        [tx["senderPublicKey"], {identify(tx): tx}]
                        for tx in pendings
                    )
                )
                dumpJson(data, path)
    except Exception as error:
        sys.stdout.write("%r\n" % error)


def _shorten(addr, n=5):
    return flask.Markup(
        '<span class="not-ellipsed">%s</span><span class="ellipsed">%s'
        '</span>' % (
            addr,
            "%s&nbsp;&hellip;&nbsp;%s" % (addr[:n], addr[-n:])
        )
    )


def checkNetwork(func):
    @wraps(func)
    def wrapper(*args, **kw):
        network = kw.get("network", "?")
        if hasattr(net, network) and \
           network != getattr(rest.cfg, network, False):
            try:
                rest.use(network)
            except Exception:
                return flask.render_template("void.html", network=network)
            return func(*args, **kw)
        else:
            return flask.render_template("void.html", network=network)
    return wrapper


@app.context_processor
def tweak():
    return dict(
        url_for=_url_for,
        symbol=getattr(rest.cfg, "symbol", "?"),
        _cfg=lambda attr: getattr(rest.cfg, attr, "?"),
        _shorten=_shorten,
        _crypto=dposlib.ark.crypto,
        _address=lambda puk: dposlib.ark.crypto.getAddress(puk),
        _json=lambda data, indent=2: json.dumps(data, indent=indent),
        _currency=lambda value, fmt="r":
            flask.Markup(
                ("%"+fmt+"&nbsp;%s") %
                (round(value, 8), rest.cfg.symbol)
            )
    )


@app.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html", network=[
        name for name in dir(net) if not name.startswith("__")
    ])


@app.route("/<string:network>", methods=["GET"])
@checkNetwork
def loadNetwork(network):
    # call to multisignature server
    resp = rest.GET.multisignature(network, peer=app.peer)
    # merge with ark server
    resp2 = loadJson(
        os.path.join(SYNCH_FOLDER, "data.%d" % rest.cfg.pubkeyHash)
    )
    if len(resp2):
        resp["success"] = True
        resp["data"] = dict(resp.get("data", {}), **resp2)

    if not len(resp.get("data", [])):
        flask.flash("no pending transaction found")

    return flask.render_template(
        "network.html", response=resp, network=network
    )


@app.route("/<string:network>/<string:wallet>", methods=["GET", "POST"])
@checkNetwork
def loadWallet(network, wallet):
    wlt = rest.GET.api.wallets(wallet).get("data", {})
    # if ms wallet never sent or received tx, publicKey is not public
    # so update manually wallet info
    if wlt.get("nonce", 0) and "multiSignature" in wlt:
        ms = wlt["multiSignature"]
        wlt["publicKey"] = dposlib.ark.crypto.getMultiSignaturePublicKey(
            ms["min"], *ms["publicKeys"]
        )

    if len(wlt):

        host_url = flask.request.host_url
        form = flask.request.form
        crypto = dposlib.core.crypto

        if flask.request.method == "POST":
            # form contains secret (https or localhost mode)
            if form.get("secret", None) not in ["", None]:
                keys = crypto.getKeys(form["secret"])
                publicKey = keys["publicKey"]
                signature = crypto.getSignatureFromBytes(
                    crypto.unhexlify(form["serial"]),
                    keys["privateKey"]
                )
            # form contains signature
            elif form.get("signature", None) not in ["", None]:
                try:
                    data = json.loads(form["signature"].strip())
                    signature = data.get("signature", "")
                    publicKey = data.get("publicKey", form["publicKey"])
                except Exception:
                    publicKey = form["publicKey"]
                    signature = form["signature"].strip()
            # form is empty
            else:
                flask.flash(
                    "Nothing found to proceed with POST request",
                    category="red"
                )

            try:
                flask.flash(
                    json.dumps(
                        client.putSignature(
                            network, form["ms_publicKey"],
                            form["id"], publicKey, signature
                        )
                    ),
                    category="yellow"
                )
            except Exception:
                pass

        # call to multisignature server
        resp = rest.GET.multisignature(
            network, wlt["publicKey"],
            peer=app.peer
        )

        # update with what is found on ark servers
        txs = loadJson(
            os.path.join(SYNCH_FOLDER, "data.%d" % rest.cfg.pubkeyHash)
        ).get(wlt["publicKey"], {})
        if len(txs):
            resp.update(txs)
            flask.flash(
                json.dumps(client.postNewTransactions(network, *txs.values())),
                category="yellow"
            )

        if not len(resp.get("data", {})):
            flask.flash("no pending transaction found")

        return flask.render_template(
            "wallet.html",
            secure="127.0.0.1" in host_url or host_url.startswith("https"),
            items=sorted(
                resp.get("data", {}).items(),
                key=lambda i: i[1]["nonce"]
            ),
            network=network, wallet=wlt
        )

    flask.flash("'%s' wallet not found" % wallet, category="red")
    # if redirect, flash messages are losed with https
    return loadNetwork(network=network)


@app.route("/<string:network>/serialize", methods=["POST"])
@checkNetwork
def serialize(network):
    if flask.request.method == "POST":
        form = flask.request.form.to_dict()
        tx = dposlib.core.Transaction(
            form,
            version=2,
            ignore_bad_fields=True
        )
        tx.senderPublicKey = form["senderPublicKey"]
        tx.amount *= 100000000
        tx.useDynamicFee(form["feeLevel"])
        tx.setFee()

        try:
            resp = json.dumps({
                "serial": dposlib.core.hexlify(
                    dposlib.core.crypto.getBytes(tx)
                )
            })
        except Exception as error:
            resp = json.dumps({
                "serial": "Serialization not possible...",
                "error": "%r" % error
            })

        return app.response_class(
            response=resp,
            status=200,
            mimetype='application/json'
        )


@app.route("/<string:network>/create", methods=["GET", "POST"])
@checkNetwork
def createWallet(network):
    return flask.render_template("building.html", network=network)


@app.route("/<string:network>/<string:wallet>/create", methods=["GET", "POST"])
@checkNetwork
def createTransaction(network, wallet):
    host_url = flask.request.host_url

    wlt = rest.GET.api.wallets(wallet).get("data", {})
    # if ms wallet never sent or received tx, publicKey is not public
    # so update manually wallet info
    if wlt.get("nonce", 0) and "multiSignature" in wlt:
        ms = wlt["multiSignature"]
        wlt["publicKey"] = dposlib.ark.crypto.getMultiSignaturePublicKey(
            ms["min"], *ms["publicKeys"]
        )

    if flask.request.method == "POST":
        crypto = dposlib.core.crypto

        form = flask.request.form.to_dict()
        tx = dposlib.core.Transaction(
            form,
            version=2,
            ignore_bad_fields=True
        )
        tx.senderPublicKey = form["senderPublicKey"]
        tx.amount *= 100000000
        tx.useDynamicFee(form["feeLevel"])
        tx.setFee()

        # form contains secret (https or localhost mode)
        if form.get("secret", None) not in ["", None]:
            keys = crypto.getKeys(form["secret"])
            publicKey = keys["publicKey"]
            signature = crypto.getSignatureFromBytes(
                crypto.unhexlify(form["serial"]),
                keys["privateKey"]
            )
        # form contains signature
        elif form.get("signature", None) not in ["", None]:
            try:
                data = json.loads(form["signature"].strip())
                publicKey = data.get("publicKey", form["publicKey"])
                signature = data.get("signature", "")
            except Exception:
                publicKey = form["senderPublicKey"]
                signature = form["signature"].strip()
        # form is empty
        else:
            signature = publicKey = None
            flask.flash(
                "Nothing found to proceed with POST request",
                category="red"
            )

        if publicKey in tx._multisignature["publicKeys"] and \
           signature is not None:
            tx["signatures"] = [
                "%02x%s" % (
                    tx._multisignature["publicKeys"].index(publicKey),
                    signature
                )
            ]
            try:
                flask.flash(
                    json.dumps(client.postNewTransactions(network, tx)),
                    category="yellow"
                )
            except Exception:
                pass

        elif publicKey is not None:
            flask.flash(
                "public key %s not owner or signature error" % publicKey,
                category="red"
            )

    return flask.render_template(
        "transfer.html",
        secure="127.0.0.1" in host_url or host_url.startswith("https"),
        network=network, wallet=wlt
    )
