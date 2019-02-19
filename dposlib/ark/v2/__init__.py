# -*- coding: utf-8 -*-
# © Toons


import pytz

from datetime import datetime

from dposlib import rest
from dposlib.ark import crypto
from dposlib.blockchain import cfg, Transaction
from dposlib.util.asynch import setInterval
from dposlib.ark.v1 import transfer, registerAsDelegate, registerSecondPublicKey, registerSecondSecret
from dposlib.ark.v2.mixin import computePayload, createWebhook, deleteWebhook
from dposlib.ark.v2 import api

DAEMON_PEERS = None
TRANSACTIONS = {
	0: "transfer",
	1: "secondSignature",
	2: "delegateRegistration",
	3: "vote",
	# 4: "multiSignature",
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
	"signatures": list,
	"id": str,
}


def select_peers():
	peers = [
		"http://%(ip)s:%(port)s" % {
			"ip":p["ip"],
			"port":cfg.ports["core-api"]
		} for p in rest.GET.api.peers().get("data", [])][:cfg.broadcast]
	if len(peers):
		cfg.peers = peers


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS

	data = rest.GET.api.v2.node.configuration().get("data", {})
	constants =  data["constants"]

	cfg.version = hex(data["version"])
	cfg.delegate = constants["activeDelegates"]
	cfg.maxlimit = constants["block"]["maxTransactions"]
	cfg.blocktime = constants["blocktime"]
	cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z"))
	cfg.blockreward = constants["reward"]/100000000.

	cfg.fees = constants["fees"]
	# on v 2.0.x dynamicFees field is in "fees" field
	cfg.doffsets = cfg.fees.get("dynamicFees", {}).get("addonBytes", {})
	# on v 2.1.x dynamicFees field is in "transactionPool" Field
	cfg.doffsets.update(data.get("transactionPool", {}).get("dynamicFees", {}).get("addonBytes", {}))
	cfg.feestats = dict([i["type"],i["fees"]] for i in data.get("feeStatistics", {}))

	cfg.explorer = data["explorer"]
	cfg.token = data["token"]
	cfg.symbol = data["symbol"]
	cfg.ports = dict([k.split("/")[-1],v] for k,v in data["ports"].items())

	cfg.headers["nethash"] = data["nethash"]
	cfg.headers["version"] = str(data["version"])
	cfg.headers["API-Version"] = "2"

	select_peers()
	DAEMON_PEERS = rotate_peers()
	Transaction.setDynamicFee()


def stop():
	global DAEMON_PEERS
	if DAEMON_PEERS != None:
		DAEMON_PEERS.set()


def computeDynamicFees(tx):
	typ_ = tx.get("type", 0)
	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	lenVF = len(vendorField)
	payload = computePayload(typ_, tx)
	T = cfg.doffsets.get(TRANSACTIONS[typ_], 0)
	signatures = "".join([tx.get("signature", ""), tx.get("signSignature", "")])
	return min(
		cfg.feestats.get(typ_, {}).get("maxFee", cfg.fees["staticFees"][TRANSACTIONS[typ_]]),
		int((T + 50 + lenVF + len(payload)) * Transaction.FMULT)
	)


def upVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"votes": ["+"+rest.GET.api.delegates(username, returnKey="data")["publicKey"] for username in usernames]
		},
	)


def downVote(*usernames):
	return Transaction(
		type=3,
		asset={
			"votes": ["-"+rest.GET.api.delegates(username, returnKey="data")["publicKey"] for username in usernames]
		},
	)


def multiSignature(*publicKeys, **kwargs): #lifetime=72, minimum=2):
	return Transaction(
		type=4,
		asset= {
			"multisignature": {
				"keysgroup": publicKeys,
				"lifetime": kwargs.get("lifetime", 72),
				"min": kwargs.get("minimum", 2),
			}
		}
	)


def nTransfer(*pairs, **kwargs): #, vendorField=None):
	return Transaction(
		type=7,
		vendorField=kwargs.get("vendorField", None),
		asset=dict(pairs)
	)
