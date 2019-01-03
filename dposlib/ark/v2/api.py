# -*- coding: utf-8 -*-
# © Toons

# ~ https://docs.ark.io/api/public/v2/


import dposlib
from dposlib.util.data import filter_dic


class Wallet(dposlib.blockchain.Wallet):
	
	def __init__(self, address, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.wallets, address, **dict({"returnKey":"data"}, **kw))


class Delegate(dposlib.blockchain.Delegate):

	def __init__(self, username, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.delegates, username, **dict({"returnKey":"data"}, **kw))

	def forged(self):
		return self._Data__dict["forged"]

	def voters(self):
		voters = [a for a in dposlib.rest.GET.api.delegates(self.username, "voters", returnKey="data") if a["balance"] not in [0, "0"]]
		return list(sorted([filter_dic(dic) for dic in voters], key=lambda e:e["balance"], reverse=True))
	
	def lastBlocks(self, limit=50):
		return dposlib.rest.GET.api.delegates(self.username, "blocks", returnKey="data")[:limit]

	def lastBlock(self):
		if self.blocks.get("last", False):
			return Block(self.blocks["last"]["id"])

	def wallet(self):
		return Wallet(self.address)


class Block(dposlib.blockchain.Block):

	def __init__(self, blk_id, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.blocks, blk_id, **dict({"returnKey":"data"}, **kw))

	def previous(self):
		return Block(self._Data__dict["previous"])

	def transactions(self):
		return dposlib.rest.GET.api.blocks(self.id, "transactions", returnKey="data")
