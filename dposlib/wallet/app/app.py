# -*- coding:utf-8 -*-
import os
import io
import sys
import time
import json
import flask
import random
import logging
import optparse
import datetime

import pytz
import dposlib

from dposlib import PY3, rest
from dposlib.blockchain import cfg

# add a parser to catch the network on startup
parser = optparse.OptionParser()
parser.add_option("-n", "--network", dest="network", type="string", default="ark", metavar="NETWORK", help="Network you want to connect with [curent : %default]")
(options, args) = parser.parse_args()

# connect to ripa network
logging.getLogger("requests").setLevel(logging.CRITICAL)
rest.use(options.network)

# needed global var
ROOT = os.path.abspath(os.path.dirname(__file__))
# private and public keys of linked account
KEYS = {}
TX_GENESIS = []
LOGGED = False

_registry_path = lambda: os.path.join(ROOT, ".registry", options.network, KEYS["publicKey"])

# create the application instance 
app = flask.Flask("DPOS wallet [%s]" % options.network) 
app.config.update(
	# 600 seconds = 10 minutes lifetime session
	PERMANENT_SESSION_LIFETIME = 300,
	# used to encrypt cookies
	# secret key is generated each time app is restarted
	SECRET_KEY = os.urandom(24),
	# JS can't access cookies
	SESSION_COOKIE_HTTPONLY = True,
	# bi use of https
	SESSION_COOKIE_SECURE = False,
	# update cookies on each request
	# cookie are outdated after PERMANENT_SESSION_LIFETIME seconds of idle
	SESSION_REFRESH_EACH_REQUEST = True,
	# 
	TEMPLATES_AUTO_RELOAD = True
)

def loadJson(path):
	"""Load JSON data from path"""
	if os.path.exists(path):
		with io.open(path) as in_:
			data = json.load(in_)
	else:
		data = {}
	return data


def dumpJson(data, path):
	"""Dump JSON data to path"""
	try:
		os.makedirs(os.path.dirname(path))
	except:
		pass
	with io.open(path, "w" if PY3 else "wb") as out:
		json.dump(data, out, indent=4)


def register(tx):
	"""Write transaction in a registry"""
	id_ = tx["id"]
	pathfile = _registry_path()
	registry = loadJson(pathfile)
	registry[tx["id"]] = tx
	dumpJson(registry, pathfile)

###
@app.context_processor
def override_url_for():
	return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
	if endpoint == 'static':
		filename = values.get('filename', None)
		if filename:
			file_path = os.path.join(app.root_path, endpoint, filename)
			values['q'] = int(os.stat(file_path).st_mtime)
	return flask.url_for(endpoint, **values)


@app.before_request
def update_session():
	"""Update wallet data if a wallet is logged in"""
	flask.session.modified = True
	if flask.session.get("data", False):
		# if session has data, address is in data
		address = flask.session["data"]["address"]
		# if wallet is a cold wallet, publicKey is not defined
		publicKey = flask.session["data"].get("publicKey", False)
		# use dposlib.rest API to get information about account and update the session cookie
		flask.session["data"].update(**rest.GET.api.accounts(address=address).get("account", {}))
		flask.session["data"].update(**rest.GET.api.delegates.get(publicKey=publicKey).get("delegate", {}))
		if publicKey:
			flask.session["data"]["voted"] = [d["username"] for d in rest.GET.api.accounts.delegates(address=address).get("delegates", [])]

###
@app.route("/", methods=["GET", "POST"])
def login():
	global KEYS, LOGGED
	flask.session["permanent"] = True

	if LOGGED:
		if not flask.session.get("data", False):
			flask.flash("Session expired !", category="warning")
			KEYS.clear()
			LOGGED = False
		else:
			flask.redirect(flask.url_for("account"))

	# 
	if flask.request.method == "POST":
		secret = flask.request.form["secret"]
		KEYS = dposlib.core.crypto.getKeys(secret)
		address = dposlib.core.crypto.getAddress(KEYS["publicKey"])
		# get info from address and public key
		account = rest.GET.api.accounts(address=address).get("account", {})
		account.update(**rest.GET.api.delegates.get(publicKey=KEYS["publicKey"]).get("delegate", {}))
		account["voted"] = [d["username"] for d in rest.GET.api.accounts.delegates(address=address).get("delegates", [])]
		account["address"]= address

		flask.session.clear()
		flask.session["data"] = account
		flask.session["secondPublicKey"] = account.get("secondPublicKey", False)
		flask.session["begin"] = (cfg.begintime - datetime.datetime(1970,1,1, tzinfo=pytz.UTC)).total_seconds()
		flask.session["explorer"] = cfg.explorer
		flask.session["symbol"] = cfg.symbol
		flask.session["dlgtnum"] = cfg.delegate
		flask.session["maxvote"] = cfg.maxvote
		#
		flask.flash('You are now logged to %s wallet...' % address, category="success")
		LOGGED = True

	# if data is set to session --> login successfull
	if flask.session.get("data", False):
		return flask.render_template("account.html")
	else:
		KEYS.clear()
		LOGGED = False
		return flask.render_template("login.html")


@app.route("/logout")
def logout():
	"""Clean up all global variables and reset session cookies"""
	global KEYS, LOGGED, CURRENT_TX, TX_GENESIS
	flask.session.clear()
	KEYS.clear()
	TX_GENESIS = []
	LOGGED = False
	return flask.redirect(flask.url_for("login"))


@app.route("/account")
def account():
	if not flask.session.get("data", False):
		return flask.redirect(flask.url_for("login"))
	else:
		return flask.render_template("account.html")


@app.route("/account/unlock", methods=["GET", "POST"])
def unlock():
	if flask.request.method == "POST":
		secondSecret = flask.request.form["secondSecret"]
		keys = dposlib.core.crypto.getKeys(secondSecret)
		if keys["publicKey"] == flask.session["secondPublicKey"]:
			KEYS["secondPublicKey"] = keys["publicKey"]
			KEYS["secondPrivateKey"] = keys["privateKey"]
			flask.session["secondPublicKey"] = False
			flask.flash('Account unlocked !', category="success")
			return flask.redirect(flask.url_for("account"))
		else:
			flask.flash('Second public key does not match !', category="error")
			return flask.redirect(flask.url_for("unlock"))
	else:
		return flask.render_template("unlock.html")


@app.route("/history")
def history():
	if not flask.session.get("data", False):
		return flask.redirect(flask.url_for("login"))
	else:
		flask.session["peer"] = random.choice(cfg.peers)
		return flask.render_template("history.html")
@app.route("/transactions")
def txlist():
	return flask.render_template("txlist.html")


@app.route("/vote")
def vote():
	if not flask.session.get("data", False):
		return flask.redirect(flask.url_for("login"))
	else:
		flask.session["peer"] = random.choice(cfg.peers)
		return flask.render_template("vote.html")
@app.route("/delegates")
def vtlist():
	return flask.render_template("vtlist.html")


@app.route("/send")
def send():
	if flask.session.get("secondPublicKey", False):
		return flask.redirect(flask.url_for("unlock"))
	else:
		if not flask.session.get("data", False):
			return flask.redirect(flask.url_for("login"))
		return flask.render_template("send.html")


# @app.route("/tx/init")
# def create():
# 	global TX_GENESIS, CURRENT_TX
# 	try:
# 		CURRENT_TX = dposlib.core.bakeTransaction(**TX_GENESIS)
# 		return flask.render_template("check.html", tx=CURRENT_TX)
# 	except Exception as e:
# 		flask.flash("API error: %s" % e.message, category="error")
# 		return flask.render_template("send.html")


# @app.route("/tx/cancel")
# def cancel():
# 	global TX_GENESIS, CURRENT_TX
# 	TX_GENESIS.clear()
# 	CURRENT_TX.clear()
# 	flask.flash("Transaction Cancelled...", category="warning")
# 	return flask.redirect(flask.url_for("account"))


# @app.route("/tx/confirm")
# def confirm():
# 	global CURRENT_TX
# 	register(CURRENT_TX)
# 	try:
# 		result = dposlib.core.sendPayload(CURRENT_TX)
# 	except Exception as e:
# 		result = {"messages": ["API error: %s" % e.message]}
# 	if len(result.get('transactions', [])):
# 		flask.flash('Transaction successfully sent:<br/>%s' % "<br/>".join(result["transactions"]), category="success")
# 	else:
# 		flask.flash("<br/>".join(result.get("messages", ["Error occured !"])), category="error")
# 	return flask.redirect(flask.url_for("account"))


