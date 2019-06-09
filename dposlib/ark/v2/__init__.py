# -*- coding: utf-8 -*-
# © Toons

import os
import pytz
from datetime import datetime

import dposlib
from dposlib import rest
from dposlib.ark import crypto
from dposlib.ark.v2 import api
from dposlib.ark.v2.mixin import serialize, serializePayload
from dposlib.blockchain import cfg, Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson, dumpJson


DAEMON_PEERS = None
TRANSACTIONS = {
	0: "transfer",
	1: "secondSignature",
	2: "delegateRegistration",
	3: "vote",
	# 4: "multiSignature",
	5: "ipfs",
	6: "timelockTransfer",
	7: "multiPayment",
	8: "delegateResignation",
}
TYPING = {
	"timestamp": int,
	"timelockType": int,
	"timelock": int,
	"type": int,
	"amount": int,
	"fee": int,
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
	api_port = cfg.ports["core-api"]
	peers = []
	candidates = rest.GET.api.peers().get("data", [])
	for candidate in candidates:
		peer = "http://%s:%s" % (candidate["ip"], api_port)
		if candidate.get("version", "") > cfg.minversion:
			synced = rest.GET.api.node.status(peer=peer).get("data")
			if isinstance(synced, dict) and synced.get("synced", False):
				peers.append(peer)
		if len(peers) >= cfg.broadcast:
			break
	if len(peers):
		cfg.peers = peers


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS

	if len(cfg.peers):
		data = rest.GET.api.v2.node.configuration().get("data", {})
		cfg.hotmode = True
		dumpJson(data, os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.cfg"))
	# if no network connection, load basic confivuration from local folder
	else:
		cfg.hotmode = False
		data = loadJson(os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.cfg"))

	# no network connetcion neither local configuration files
	if data == {}:
		raise Exception("Initialization error")
	else:
		cfg.marker = hex(data["version"])[2:]
		cfg.explorer = data["explorer"]
		cfg.pubKeyHash = data["version"]
		cfg.token = data["token"]
		cfg.symbol = data["symbol"]
		cfg.ports = dict([k.split("/")[-1],v] for k,v in data["ports"].items())
		cfg.headers["nethash"] = data["nethash"]
		cfg.headers["API-Version"] = "2"

		constants =  data["constants"]
		cfg.delegate = constants["activeDelegates"]
		cfg.maxlimit = constants["block"]["maxTransactions"]
		cfg.maxTransactions = constants["block"]["maxTransactions"]
		cfg.blocktime = constants["blocktime"]
		cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z"))
		cfg.blockreward = constants["reward"]/100000000.
		cfg.fees = constants["fees"]

		cfg.feestats = dict([i["type"],i["fees"]] for i in data.get("feeStatistics", {}))
		# on v 2.0.x dynamicFees field is in "fees" field
		cfg.doffsets = cfg.fees.get("dynamicFees", {}).get("addonBytes", {})
		# on v 2.1.x dynamicFees field is in "transactionPool" Field
		cfg.doffsets.update(data.get("transactionPool", {}).get("dynamicFees", {}).get("addonBytes", {}))
		# on v 2.4.x wif and slip44 are provided by network
		if "wif" in data: cfg.wif = hex(data["wif"])[2:]
		if "slip44" in data: cfg.slip44 = str(data["slip44"])

		# since ark v2.4 fee statistic moved to ~/api/node/fees endpoint
		if cfg.feestats == {}:
			if len(cfg.peers):
				fees = rest.GET.api.node.fees()
				dumpJson(fees, os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.fee"))
			else:
				fees = loadJson(os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.fee"))
			cfg.feestats = dict([int(i["type"]), {
				"avgFee": int(i["avg"]),
				"minFee": int(i["min"]),
				"maxFee": int(i["min"]),
				"medFee": int(i["median"])
			}] for i in fees.get("data", []))

		if len(cfg.peers):
			DAEMON_PEERS = rotate_peers()
		Transaction.useDynamicFee()


def stop():
	global DAEMON_PEERS
	if DAEMON_PEERS != None:
		DAEMON_PEERS.set()


# https://github.com/ArkEcosystem/AIPs/blob/master/AIPS/aip-16.md
def computeDynamicFees(tx):
	typ_ = tx.get("type", 0)
	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	lenVF = len(vendorField)
	payload = serializePayload(tx)
	T = cfg.doffsets.get(TRANSACTIONS[typ_], 0)
	signatures = "".join([tx.get("signature", ""), tx.get("signSignature", "")])
	return min(
		cfg.feestats.get(typ_, {}).get("maxFee", cfg.fees["staticFees"][TRANSACTIONS[typ_]]),
		int((T + 50 + lenVF + len(payload)) * Transaction.FMULT)
	)


def broadcastTransactions(*transactions, **params):
	serialized = params.pop("serialzed", False)
	chunk_size = params.pop("chunk_size", 20)
	report = []
	if serialized:
		transactions = [serialize(tx) for tx in transactions]
		for chunk in [transactions[i:i+chunk_size] for i in range(0, len(transactions), chunk_size)]:
			pass
	else:
		for chunk in [transactions[i:i+chunk_size] for i in range(0, len(transactions), chunk_size)]:
			response = rest.POST.api.transactions(transactions=chunk)
			report.append(response)
	return None if len(report) == 0 else \
		   report[0] if len(report) == 1 else \
		   report


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


def registerIPFS(dag):
	return Transaction(
		type=5,
		asset={
			"ipfs": {"dag": dag}
		}
	)


def timelockTransfer(amount, address, lockvalue, locktype="timestamp", vendorField=None):
	return Transaction(
		type=6,
		amount=amount*100000000,
		recipientId=address,
		vendorField=vendorField,
		timelock=lockvalue,
		timelockType={
			"timestamp":0,
			"blockheight":1
		}[locktype]
	)


def multiPayment(*pairs, **kwargs):
	return Transaction(
		type=7,
		vendorField=kwargs.get("vendorField", None),
		asset={
			"payments": [
				{"amount":a, "recipientId":r} for r,a in pairs
			]
		}
	)


def delegateResignation():
	return Transaction(
		type=8
	)
