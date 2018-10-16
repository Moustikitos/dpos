# -*- coding: utf-8 -*-
# © Toons


import pytz

from datetime import datetime

from dposlib import rest
from dposlib.ark import crypto
from dposlib.ark.v1 import api
from dposlib.blockchain import cfg, Transaction
from dposlib.util.asynch import setInterval


DAEMON_PEERS = None
TRANSACTIONS = {
	0: "send",
	1: "secondsignature",
	2: "delegate",
	3: "vote",
}
TYPING = {
	"timestamp": int,
	"type": int,
	"amount": int,
	"senderPublicKey": str,
	"recipientId": str,
	"senderId": str,
	"vendorField": str,
	"asset": dict,
	"signature": str,
	"signSignature": str,
	"id": str,
}


def select_peers():
	version = rest.GET.api.peers.version(returnKey='version') or '0.0.0'
	height = rest.GET.api.blocks.getHeight(returnKey='height') or 0
	if isinstance(height, dict) or isinstance(version, dict):
		return

	peers = rest.GET.peer.list().get('peers', [])
	good_peers = []
	for peer in peers:
		if (
			peer.get("delay", 6000) <= cfg.timeout * 1000 and peer.get("version") == version and
			peer.get("height", -1) > height - 10
		):
			good_peers.append(peer)

	good_peers = sorted(good_peers, key=lambda e: e["delay"])

	min_selection = getattr(cfg, "broadcast", 0)
	selection = []
	for peer in good_peers:
		peer = "http://{ip}:{port}".format(**peer)
		if rest.check_latency(peer):
			selection.append(peer)

		if len(selection) >= min_selection:
			break

	if len(selection) >= min_selection:
		cfg.peers = selection


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	Transaction.setStaticFee()


	cfg.begintime = datetime(*cfg.begintime, tzinfo=pytz.UTC)
	response = rest.GET.api.loader.autoconfigure()
	if response["success"]:
		network = response["network"]
		if "version" not in cfg.headers:
			cfg.headers["version"] = str(network.pop('version'))
		cfg.headers["nethash"] = network.pop('nethash')
		cfg.headers["API-Version"] = "1"
		cfg.__dict__.update(network)
		cfg.fees = rest.GET.api.blocks.getFees()["fees"]
		# select peers immediately and keep refreshing them in a thread so we
		# are sure we make requests to working peers
		select_peers()
		DAEMON_PEERS = rotate_peers()
	else:
		raise Exception("Initialization error with peer %s" % response.get("peer", "???"))


def stop():
	global DAEMON_PEERS
	if DAEMON_PEERS != None:
		DAEMON_PEERS.set()


def transfer(amount, address, vendorField=None):
	return Transaction(
		type=0,
		amount=amount*100000000,
		recipientId=address,
		vendorField=vendorField
	)


def registerSecondSecret(secondSecret):
	return registerSecondPublicKey(crypto.getKeys(secondSecret)["publicKey"])

def registerSecondPublicKey(secondPublicKey):
	return Transaction(
		type=1,
		asset={
			"signature": {
				"publicKey": secondPublicKey
			}
		}
	)


def registerAsDelegate(username):
	return Transaction(
		type=2,
		asset={
			"delegate": {
				"username": username
			}
		}
	)


def upVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"votes": {
				"username": ["+"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
			}
		}
	)


def downVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"votes": {
				"username": ["-"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
			}
		}
	)

