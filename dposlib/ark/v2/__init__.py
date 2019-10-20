# -*- coding: utf-8 -*-
# © Toons

# api endpoint to locate blockchain configuration
__CFG__ = "api/node/configuration"
__FEE__ = "api/node/fees"

import os
import pytz
from datetime import datetime

import dposlib
from dposlib import rest
from dposlib.ark import crypto
from dposlib.ark.v2 import api
from dposlib.ark.v2.mixin import loadPages, deltas
from dposlib.blockchain import cfg, Transaction
from dposlib.util.asynch import setInterval
from dposlib.util.data import loadJson, dumpJson


DAEMON_PEERS = None
TRANSACTIONS = {
	0: "transfer",
	1: "secondSignature",
	2: "delegateRegistration",
	3: "vote",
	4: "multiSignature",
	5: "ipfs",
	6: "multiPayment",
	7: "delegateResignation",
	8: "htlclock",
	9: "htlcclaim",
	10: "htlcrefund",
}
TYPING = {
	"amount": int,
	"asset": dict,
	"expiration": int,
	"fee": int,
	"id": str,
	"nonce": int,
	"recipientId": str,
	"senderPublicKey": str,
	"senderId": str,
	"signature": str,
	"signSignature": str,
	"signatures": list,
	"timestamp": int,
	"timelockType": int,
	"timelock": int,
	"type": int,
	"typeGroup": int,
	"vendorField": str,
	"version": int,
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
	cfg.headers["API-Version"] = "2"
	
	if len(cfg.peers):
		data = rest.GET(*__CFG__.split("/")).get("data", {})
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
		cfg.pubKeyHash = data["version"]
		cfg.token = data["token"]
		cfg.symbol = data["symbol"]
		cfg.ports = dict([k.split("/")[-1],v] for k,v in data["ports"].items())
		cfg.headers["nethash"] = data["nethash"]
		cfg.explorer = data["explorer"]

		constants =  data["constants"]
		cfg.delegate = constants["activeDelegates"]
		cfg.maxlimit = constants["block"]["maxTransactions"]
		cfg.maxTransactions = constants["block"]["maxTransactions"]
		cfg.blocktime = constants["blocktime"]
		cfg.begintime = pytz.utc.localize(datetime.strptime(constants["epoch"], "%Y-%m-%dT%H:%M:%S.000Z"))
		cfg.blockreward = constants["reward"]/100000000.
		cfg.fees = constants["fees"]

		# dynamic fee management
		# on v2.0 dynamicFees are in "fees" field
		cfg.doffsets = cfg.fees.get("dynamicFees", {}).get("addonBytes", {})
		# on v2.1 dynamicFees are in "transactionPool" field
		cfg.doffsets.update(data.get("transactionPool", {}).get("dynamicFees", {}).get("addonBytes", {}))
		# before ark v2.4 dynamicFees statistics are in "feeStatistics" field
		cfg.feestats = dict([i["type"],i["fees"]] for i in data.get("feeStatistics", {}))
		# since ark v2.4 fee statistic moved to ~/api/node/fees endpoint
		if cfg.feestats == {}:
			if len(cfg.peers):
				fees = rest.GET(*__FEE__.split("/"))
				dumpJson(fees, os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.fee"))
			else:
				fees = loadJson(os.path.join(dposlib.ROOT, ".cold", cfg.network+".v2.fee"))
			cfg.feestats = dict([
				int(i["type"]), {
					"avgFee": int(i["avg"]),
					"minFee": int(i["min"]),
					"maxFee": int(i["min"]),
				}
			] for i in fees.get("data", []))

		# since ark v2.4 wif and slip44 are provided by network
		if "wif" in data: cfg.wif = hex(data["wif"])[2:]
		if "slip44" in data: cfg.slip44 = str(data["slip44"])

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
	version = tx.get("version", 0x01)

	vendorField = tx.get("vendorField", "")
	vendorField = vendorField.encode("utf-8") if not isinstance(vendorField, bytes) else vendorField
	lenVF = len(vendorField)
	payload = crypto.serializePayload(tx)
	T = cfg.doffsets.get(TRANSACTIONS[typ_], 0)
	signatures = "".join([tx.get("signature", ""), tx.get("signSignature", "")])
	return int((T + 50 + (4 if version >= 0x02 else 0) + lenVF + len(payload)) * Transaction.FMULT)
	
	# return min(
	# 	cfg.feestats.get(typ_, {}).get("maxFee", cfg.fees["staticFees"][TRANSACTIONS[typ_]]),
	# 	int((T + 50 + (4 if version >= 0x02 else 0) + lenVF + len(payload)) * Transaction.FMULT)
	# )


def broadcastTransactions(*transactions, **params):
	serialized = params.pop("serialized", False)
	chunk_size = params.pop("chunk_size", 20)
	report = []
	if serialized:
		transactions = [crypto.serialize(tx) for tx in transactions]
		for chunk in [transactions[i:i+chunk_size] for i in range(0, len(transactions), chunk_size)]:
			pass
	else:
		for chunk in [transactions[i:i+chunk_size] for i in range(0, len(transactions), chunk_size)]:
			response = rest.POST.api.transactions(transactions=chunk)
			report.append(response)
	return None if len(report) == 0 else \
		   report[0] if len(report) == 1 else \
		   report


def transfer(amount, address, expiration=0, vendorField=None, version=1):
	return Transaction(
		type=0,
		amount=amount*100000000,
		recipientId=address,
		vendorField=vendorField,
		version=version,
		expiration=None if version < 2 else expiration
	)


def registerSecondSecret(secondSecret, version=1):
	return registerSecondPublicKey(crypto.getKeys(secondSecret)["publicKey"], version=version)


def registerSecondPublicKey(secondPublicKey, version=1):
	return Transaction(
		type=1,
		version=version,
		asset={
			"signature": {
				"publicKey": secondPublicKey
			}
		}
	)


def registerAsDelegate(username, version=1):
	return Transaction(
		type=2,
		version=version,
		asset={
			"delegate": {
				"username": username
			}
		}
	)


def upVote(*usernames, **kwargs): #, version=1):
	return Transaction(
		type=3,
		version=kwargs.get("version", 1),
		asset={
			"votes": ["+"+rest.GET.api.delegates(username, returnKey="data")["publicKey"] for username in usernames]
		},
	)


def downVote(*usernames, **kwargs): #, version=1):
	return Transaction(
		type=3,
		version=kwargs.get("version", 1),
		asset={
			"votes": ["-"+rest.GET.api.delegates(username, returnKey="data")["publicKey"] for username in usernames]
		},
	)


def registerMultiSignature(min, *publicKeys, **kwargs): #, version=1):
	return Transaction(
		version=kwargs.get("version", None),
		type=4,
		asset={
			"multiSignature": {
				"min": min,
				"publicKeys": publicKeys
			}
		},
	)


def registerIpfs(ipfs):
	return Transaction(
		version=2,
		type=5,
		asset={
			"ipfs": ipfs
		}
	)


def multiPayment(*pairs, **kwargs):
	return Transaction(
		version=2,
		type=6,
		vendorField=kwargs.get("vendorField", None),
		asset={
			"payments": [
				{"amount":a, "recipientId":r} for r,a in pairs
			]
		}
	)


def delegateResignation():
	return Transaction(
		version=2,
		type=7
	)


def htlcLock(amount, address, expiration, secretHash, vendorField=None):
	return Transaction(
		version=2,
		type=8,
		amount=amount*100000000,
		recipientId=address,
		vendorField=vendorField,
		asset={
			"lock":{
				"secretHash":secretHash,
				"expiration":expiration
			}
		}
	)


def htlcClaim(lockTransactionId, unLockSecret):
	return Transaction(
		version=2,
		type=9,
		asset={
			"claim":{
				"lockTransactionId":lockTransactionId,
				"unLockSecret":unLockSecret
			}
		}
	)


def htlcRefund(lockTransactionId):
	return Transaction(
		version=2,
		type=10,
		asset={
			"refund":{
				"lockTransactionId":lockTransactionId,
			}
		}
	)


__all__ = [
	"crypto",
	"Transaction",
	"loadPages", "broadcastTransactions",
	"transfer", "registerSecondSecret", "registerSecondPublicKey", "registerAsDelegate", "upVote", "downVote",
	"registerMultiSignature", "registerIpfs", "multiPayment", "delegateResignation",
	"htlcLock", "htlcClaim", "htlcRefund"
]
