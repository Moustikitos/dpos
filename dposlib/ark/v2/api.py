# -*- coding: utf-8 -*-
# © Toons

# ~ https://docs.ark.io/api/public/v2/


import dposlib

from dposlib import rest
from dposlib.util.data import filter_dic
from dposlib.blockchain import Data, Transaction


class Wallet(Data):
	
	link = staticmethod(Transaction.link)
	unlink = staticmethod(Transaction.unlink)

	def __init__(self, address, **kw):
		Data.__init__(self, rest.GET.api.wallets, address, **dict({"returnKey":"data"}, **kw))

	def lastTransactions(self, limit=50):
		received, sent, count = [], [], 0
		while count < limit:
			sent.extend(rest.GET.api.transactions(senderId=self.address, orderBy="timestamp:desc", returnKey="data", offset=len(sent)))
			received.extend(rest.GET.api.transactions(recipientId=self.address, orderBy="timestamp:desc", returnKey="data", offset=len(received)))
			tmpcount = len(sent)+len(received)
			count = limit if count == tmpcount else tmpcount
		return [filter_dic(dic) for dic in sorted(received+sent, key=lambda e:e["timestamp"].get("epoch", None), reverse=True)[:limit]]

	def send(self, amount, recipientId, vendorField=None, **kw):
		# create a type-1-transaction
		tx = Transaction(type=0, amount=amount*100000000, recipientId=recipientId, vendorField=vendorField, **kw)
		# sign if a public and private keys exists
		try: tx.finalize()
		# if no key: return orphan tx
		except: return tx
		# else broadcast tx
		else: return rest.POST.api.transactions(transactions=[tx])


class Delegate(Data):

	def __init__(self, username, **kw):
		Data.__init__(self, rest.GET.api.delegates, username, **dict({"returnKey":"data"}, **kw))

	def forged(self):
		result = filter_dic(rest.GET.api.delegates.forging.getForgedByAccount(generatorPublicKey=self.publicKey))
		result.pop("success", False)
		return result

	def voters(self):
		voters = [a for a in rest.GET.api.delegates(self.username, "voters", returnKey="data") if a["balance"] not in [0, "0"]]
		return list(sorted([filter_dic(dic) for dic in voters], key=lambda e:e["balance"], reverse=True))
	
	def lastBlocks(self, limit=50):
		return rest.GET.api.delegates(self.username, "blocks", returnKey="data")[:limit]

	def lastBlock(self):
		return Block(self.blocks["last"]["id"])


class Block(Data):

	def __init__(self, blk_id, **kw):
		Data.__init__(self, rest.GET.api.blocks, blk_id, **dict({"returnKey":"data"}, **kw))

	def previous(self):
		return Block(self._Data__dict["previous"])

	def transactions(self):
		return rest.GET.api.blocks(self.id, "transactions", returnKey="data")
