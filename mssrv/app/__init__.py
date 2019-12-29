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
    # bi use of https
    SESSION_COOKIE_SECURE=False,
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
        flask.flash("no pending transaction found", category="info")

    return flask.render_template("index.html", response=resp, network=network)


@app.route("/<string:network>/<string:wallet>", methods=["GET", "POST"])
def loadWallet(network, wallet):
    # first filter
    if network not in dir(net):
        return ""
    elif network != getattr(rest.cfg, "network", False):
        rest.use(network)
    wlt = rest.GET.api.wallets(wallet).get("data", [])

    if len(wlt):
        if flask.request.method == "POST":
            if flask.request.form["secret"] in ["", None]:
                flask.flash("No secret found", category="error")
            else:
                resp = {}
                form = flask.request.form
                crypto = dposlib.core.crypto
                keys = crypto.getKeys(form["secret"])
                signature = crypto.getSignatureFromBytes(
                    crypto.unhexlify(form["serial"]),
                    keys["privateKey"]
                )
                flask.flash(
                    json.dumps(
                        rest.PUT.multisignature(
                            network, form["ms_publicKey"], "put",
                            peer=app.peer,
                            info={
                                "publicKey": keys["publicKey"],
                                "signature": signature,
                                "id": form["id"]
                            }
                        )
                    )
                )

        # call to multisignature server
        resp = rest.GET.multisignature(
            network, wlt["publicKey"],
            peer=app.peer
        )

        if not len(resp.get("data", [])):
            flask.flash("no pending transaction found", category="info")

        return flask.render_template(
            "wallet.html",
            response=resp, network=network, wallet=wlt
        )

    flask.flash("'%s' wallet not found" % wallet)
    return flask.redirect(
        flask.url_for("loadNetwork", response={}, network=network)
    )


def initWallet():
    pass


def initTransaction():
    pass
