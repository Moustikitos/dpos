# -*- encoding:utf-8 -*-
import os
import sys
import time
import flask
import random
import logging
import optparse
import datetime
import webbrowser

import pytz
import arky
from arky import rest
from arky import cfg

# add a parser to catch the network on startup
parser = optparse.OptionParser()
parser.add_option("-n", "--network", dest="network", type="string", default="ark", metavar="NETWORK", help="Network you want to connect with [curent : %default]")
(options, args) = parser.parse_args()

# connect to ripa network
logging.getLogger("requests").setLevel(logging.CRITICAL)
rest.use(options.network)

# needed global var
ROOT = os.path.abspath(os.path.dirname(__file__))
KEYS = {}
ACCOUNT = {}
LOGGED = False

# create the application instance 
app = flask.Flask("DPOS wallet") 
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
	TEMPLATES_AUTO_RELOAD = True
)


@app.before_request
def before_request():
	"""Reset cookie timeout on each request"""
	flask.session.modified = True
	if flask.session.get("data", False):
		flask.session["data"].update(**rest.GET.api.accounts(address=flask.session["data"]["address"]).get("account", {}))
		flask.session["data"].update(**rest.GET.api.delegates.get(publicKey=KEYS["publicKey"]).get("delegate", {}))

	
@app.route("/", methods=["GET", "POST"])
def login():
	global KEYS, ACCOUNT, LOGGED
	flask.session["permanent"] = True

	# if LOGGED true and login called
	# --> session expired
	if LOGGED:
		flask.flash("Session expired !", category="warning")
	
	if flask.request.method == "POST":
		# check if address matches with publicKey computed from secret
		address = flask.request.form["address"]
		secret = flask.request.form["secret"]
		KEYS = arky.core.crypto.getKeys(secret)
		ACCOUNT = rest.GET.api.accounts(address=address).get("account", {})
		ACCOUNT.update(**rest.GET.api.delegates.get(publicKey=KEYS["publicKey"]).get("delegate", {}))
		ACCOUNT["voted"] = rest.GET.api.accounts.delegates(address=address).get("delegates", [])

		# if address matches with publicKey, set session cookies 
		if address == arky.core.crypto.getAddress(KEYS["publicKey"]):
			flask.flash('You are now logged to %s wallet...' % address, category="success")
			flask.session["data"] = ACCOUNT
			LOGGED = True
		# 
		else:
			flask.session.pop("data", None)
			flask.flash('Login failed !', category="error")
		flask.session["secondPublicKey"] = ACCOUNT.get("secondPublicKey", False)
	
	if flask.session.get("data", False):
		return flask.render_template("account.html")
	else:
		KEYS.clear()
		ACCOUNT.clear()
		LOGGED = False
		return flask.render_template("login.html")

@app.route("/logout")
def logout():
	global KEYS, ACCOUNT, LOGGED
	flask.session.clear()
	# .pop("secondPublicKey", None)
	# flask.session.pop("_flashes", None)
	# flask.session.pop("explorer", None)
	# flask.session.pop("begin", None)
	# flask.session.pop("peer", None)
	# flask.session.pop("data", None)
	KEYS.clear()
	ACCOUNT.clear()
	LOGGED = False
	return flask.render_template("login.html")

@app.route("/send", methods=["POST", "GET"])
def send():

	if flask.request.method == "POST":
		if "2ndSecret" in flask.request.form:
			secondSecret = flask.request.form["secondSecret"]
			keys = arky.core.crypto.getKeys(secondSecret)
			if keys["publicKey"] == flask.session["secondPublicKey"]:
				KEYS["secondPublicKey"] = keys["publicKey"]
				KEYS["secondPrivateKey"] = keys["privateKey"]
				flask.session["secondPublicKey"] = False
				flask.flash('Second public key set !', category="success")
			else:
				flask.flash('Second public key does not match !', category="error")
		
		else:
			args = dict(
				recipientId=flask.request.form["recipientId"],
				amount=float(flask.request.form["amount"])*100000000,
				vendorField=flask.request.form["vendorField"],
				publicKey=KEYS.get("publicKey", None),
				privateKey=KEYS.get("privateKey", None),
				secondPrivateKey=KEYS.get("secondPrivateKey", None)
			)
			try:
				result = arky.core.sendTransaction(**args)
			except Exception as e:
				result = {"messages": ["API error: %s" % e.message]}
			if len(result.get('transactions', [])):
				flask.flash('Transaction successfully sent !', category="success")
			else:
				flask.flash("<br/>".join(result.get("messages", ["Error occured !"])), category="error")
		return flask.render_template("send.html")
	else:
		if not flask.session.get("data", False):
			return flask.redirect(flask.url_for("login"))
		return flask.render_template("send.html")

@app.route("/account")
def account():
	if not flask.session.get("data", False):
		return flask.redirect(flask.url_for("login"))
	else:
		return flask.render_template("account.html")

@app.route("/history")
def history():
	if not flask.session.get("data", False):
		return flask.redirect(flask.url_for("login"))
	else:
		flask.session["peer"] = random.choice(cfg.peers)
		flask.session["explorer"] = cfg.explorer
		flask.session["begin"] = (cfg.begintime - datetime.datetime(1970,1,1, tzinfo=pytz.UTC)).total_seconds()
		return flask.render_template("history.html")

@app.route("/vote")
def vote():
	if not flask.session.get("data", False):
		return flask.redirect(flask.url_for("login"))
	else:
		return flask.render_template("vote.html")

@app.route("/transactions")
def txlist():
	return flask.render_template("txlist.html")

##
@app.context_processor
def override_url_for():
	return dict(url_for=dated_url_for)
	
def dated_url_for(endpoint, **values):
	if endpoint == 'static':
		filename = values.get('filename', None)
		if filename:
			file_path = os.path.join(app.root_path,
									 endpoint, filename)
			values['q'] = int(os.stat(file_path).st_mtime)
	return flask.url_for(endpoint, **values)
