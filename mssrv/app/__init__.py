# -*- coding:utf-8 -*-
# (C) Toons MIT Licence

import os
import json
import flask

import dposlib
from dposlib import rest, net


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
app.peer = "http://127.0.0.1:5000"


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


def _shorten(addr, n=5):
    return flask.Markup(
        '<span class="not-ellipsed">%s</span><span class="ellipsed">%s'
        '</span>' % (
            addr,
            "%s&nbsp;&hellip;&nbsp;%s" % (addr[:n], addr[-n:])
        )
    )


@app.context_processor
def tweak():
    return dict(
        url_for=_url_for,
        _shorten=_shorten,
        _crypto=dposlib.core.crypto,
        _address=lambda puk: dposlib.core.crypto.getAddress(puk),
        _json=lambda data, indent=2: json.dumps(data, indent=indent),
        _currency=lambda value, fmt="r":
            flask.Markup(
                ("%"+fmt+"&nbsp;%s") %
                (round(value, 8), dposlib.core.cfg.symbol)
            )
    )


@app.route("/<string:network>", methods=["GET"])
def loadNetwork(network):
    # first filter
    if network not in dir(net):
        return ""
    elif network != getattr(rest.cfg, "network", False):
        rest.use(network)

    # call to multisignature server
    resp = rest.GET.multisignature(network, peer=app.peer)

    if not len(resp.get("data", [])):
        flask.flash("no pending transaction found")

    return flask.render_template("index.html", response=resp, network=network)


@app.route("/<string:network>/<string:wallet>", methods=["GET", "POST"])
def loadWallet(network, wallet):
    # first filter
    if network not in dir(net):
        return ""
    elif network != getattr(rest.cfg, "network", False):
        rest.use(network)

    host_url = flask.request.host_url
    wlt = rest.GET.api.wallets(wallet).get("data", [])
    crypto = dposlib.core.crypto
    form = flask.request.form

    if len(wlt):

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
            # print({
            #                     "publicKey": publicKey,
            #                     "signature": signature,
            #                     "id": form["id"]
            #                 })
            flask.flash(
                json.dumps(
                    rest.PUT.multisignature(
                        network, form["ms_publicKey"], "put",
                        peer=app.peer,
                        info={
                            "publicKey": publicKey,
                            "signature": signature,
                            "id": form["id"]
                        }
                    )
                )
            )
        except Exception:
            pass
        finally:
            # call to multisignature server
            resp = rest.GET.multisignature(
                network, wlt["publicKey"],
                peer=app.peer
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
    return flask.redirect(
        flask.url_for("loadNetwork", response={}, network=network)
    )


@app.route("/<string:network>/create", methods=["GET", "POST"])
def createWallet(network):
    pass


@app.route("/<string:network>/<string:wallet>/create", methods=["GET", "POST"])
def createTransaction(network, wallet):
    pass

