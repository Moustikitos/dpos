# -*- coding: utf-8 -*-
# © Toons
# ~ https://docs.ark.io/archive/api/public-v1/

import dposlib
from dposlib.util.data import filter_dic


class Wallet(dposlib.blockchain.Wallet):

	def __init__(self, address, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.accounts, **dict({"address":address, "returnKey":"account"}, **kw))

	def transactions(self, limit=50):
		received, sent, count = [], [], 0
		while count < limit:
			sent.extend(dposlib.rest.GET.api.transactions(senderId=self.address, orderBy="timestamp:desc", returnKey="transactions", offset=len(sent)))
			received.extend(dposlib.rest.GET.api.transactions(recipientId=self.address, orderBy="timestamp:desc", returnKey="transactions", offset=len(received)))
			tmpcount = len(sent)+len(received)
			count = limit if count == tmpcount else tmpcount
		return [filter_dic(dic) for dic in sorted(received+sent, key=lambda e:e.get("timestamp", None), reverse=True)[:limit]]


class NanoS(dposlib.blockchain.NanoS):

	def __init__(self, network, account, index, **kw):
		# aip20 : https://github.com/ArkEcosystem/AIPs/issues/29
		self.derivationPath = "44'/%s'/%s'/%s'/%s" % (cfg.slip44, getattr(dposlib.rest.cfg, "aip20", network), account, index)
		self.address = dposlib.core.crypto.getAddress(ldgr.getPublicKey(ldgr.parseBip32Path(self.derivationPath)))
		self.debug = kw.pop("debug", False)
		Wallet.__init__(self, self.address, **kw)


class Delegate(dposlib.blockchain.Data):
	
	def __init__(self, username, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.delegates.get, **dict({"username":username, "returnKey":"delegate"}, **kw))

	def getWallet(self):
		return Wallet(self.address)

	def forged(self):
		result = filter_dic(dposlib.rest.GET.api.delegates.forging.getForgedByAccount(generatorPublicKey=self.publicKey))
		result.pop("success", False)
		return result

	def voters(self):
		voters = [a for a in dposlib.rest.GET.api.delegates.voters(publicKey=self.publicKey, returnKey="accounts") if a["balance"] not in [0, "0"]]
		return list(sorted([filter_dic(dic) for dic in voters], key=lambda e:e["balance"], reverse=True))
	
	def lastBlock(self):
		blocks = [blk for blk in dposlib.rest.GET.api.blocks(returnKey="blocks") if blk["generatorId"] == self.address]
		if len(blocks):
			return Block(blocks[0]["id"])


class Block(dposlib.blockchain.Data):

	def __init__(self, blk_id, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.blocks.get, **dict({"id":blk_id, "returnKey":"block"}, **kw))

	def previous(self):
		return Block(self.previousBlock)

	def transactions(self):
		return dposlib.rest.GET.api.transactions(blockId=self.id, returnKey="transactions")
