# -*- coding: utf-8 -*-
# © Toons


import pytz

from datetime import datetime

from dposlib import rest
from dposlib.ark import crypto
from dposlib.blockchain import cfg, Transaction
from dposlib.util.asynch import setInterval

from dposlib.ark.v2.mixin import computePayload

DAEMON_PEERS = None
TRANSACTIONS = {
	0: "transfer",
	1: "delegateRegistration",
	2: "secondSignature",
	3: "vote",
	4: "multiSignature",
	# 5: "ipfs",
	# 6: "timelockTransfer",
	# 7: "multiPayment",
	# 8: "delegateResignation",
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
	peers = [
		"http://%(ip)s:%(port)s" % {
			"ip":p["ip"],
			"port":cfg.ports["@arkecosystem/core-api"]
		} for p in rest.GET.api.peers().get("data", [])][:cfg.broadcast]
	if len(peers):
		cfg.peers = peers


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	Transaction.DFEES = True

	data = rest.GET.api.v2.node.configuration().get("data", {})

	constants =  data["constants"]
	cfg.blocktime = constants["blocktime"]
	cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:00.000Z"))
	cfg.delegate = constants["activeDelegates"]

	cfg.headers["nethash"] = data["nethash"]
	cfg.headers["version"] = data["version"]
	cfg.fees = constants["fees"]
	cfg.doffsets = constants["dynamicOffsets"]
	cfg.explorer = data["explorer"]
	cfg.token = data["token"]
	cfg.symbol = data["symbol"]
	cfg.ports = data["ports"]

	select_peers()
	DAEMON_PEERS = rotate_peers()


def stop():
	global DAEMON_PEERS
	Transaction.DFEES = False
	DAEMON_PEERS.set()


def setDynamicFees(tx):
	typ_ = tx.get("type", 0)
	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	lenVF = len(vendorField)
	payload = computePayload(typ_, tx)
	T = cfg.doffsets[
		{	0: "transfer",
			1: "delegateRegistration",
			2: "secondSignature",
			3: "vote",
			4: "multiSignature",
			5: "ipfs",
			6: "timelockTransfer",
			7: "multiPayment",
			8: "delegateResignation",
		}[typ_]
	]
	dict.__setitem__(tx, "fee", (T + 50 + lenVF + len(payload)) * Transaction.FMULT)


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
		asset={"secondPublicKey":secondPublicKey},
	)


def registerAsDelegate(username):
	return Transaction(
		type=2,
		asset={
			"username":username
		},
	)


def upVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"delegatePublicKeys":["01"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
		},
	)


def downVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"delegatePublicKeys":["00"+rest.GET.api.delegates.get(username=username, returnKey="delegate")["publicKey"] for username in usernames]
		},
	)

