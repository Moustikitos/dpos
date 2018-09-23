# -*- coding: utf-8 -*-
# © Toons

# ~ https://lisk.io/documentation/lisk-core/user-guide/api/0-9

import dposlib

from dposlib import rest
from dposlib.util.data import filter_dic
from dposlib.blockchain import Data, Transaction


class Wallet(Data):
	
	link = staticmethod(Transaction.link)
	unlink = staticmethod(Transaction.unlink)

	def __init__(self, address, **kw):
		Data.__init__(self, rest.GET.api.accounts, **dict({"address":address, "returnKey":"account"}, **kw))

	def lastTransactions(self, limit=50):
		received, sent, count = [], [], 0
		while count < limit:
			sent.extend(rest.GET.api.transactions(senderId=self.address, orderBy="timestamp:desc", returnKey="transactions", offset=len(sent)))
			received.extend(rest.GET.api.transactions(recipientId=self.address, orderBy="timestamp:desc", returnKey="transactions", offset=len(received)))
			tmpcount = len(sent)+len(received)
			count = limit if count == tmpcount else tmpcount
		return [filter_dic(dic) for dic in sorted(received+sent, key=lambda e:e.get("timestamp", None), reverse=True)[:limit]]

	def send(self, amount, recipientId, **kw):
		# create a type-1-transaction
		tx = Transaction(type=0, amount=amount*100000000, recipientId=recipientId, **kw)
		# sign if a public and private keys exists
		try: tx.finalize()
		# if no key: return orphan tx
		except: return tx
		# else broadcast tx
		else: return rest.POST.peer.transactions(transactions=[tx])


class Delegate(Data):

	def __init__(self, username, **kw):
		Data.__init__(self, rest.GET.api.delegates.get, **dict({"username":username, "returnKey":"delegate"}, **kw))

	def forged(self):
		result = filter_dic(rest.GET.api.delegates.forging.getForgedByAccount(generatorPublicKey=self.publicKey))
		result.pop("success", False)
		return result

	def voters(self):
		voters = [a for a in rest.GET.api.delegates.voters(publicKey=self.publicKey, returnKey="accounts") if a["balance"] not in [0, "0"]]
		return list(sorted([filter_dic(dic) for dic in voters], key=lambda e:e["balance"], reverse=True))
	
	def lastBlock(self):
		blocks = [blk for blk in rest.GET.api.blocks(returnKey="blocks") if blk["generatorId"] == self.address]
		if len(blocks):
			return Block(blocks[0]["id"])


class Block(Data):

	def __init__(self, blk_id, **kw):
		Data.__init__(self, rest.GET.api.blocks.get, **dict({"id":blk_id, "returnKey":"block"}, **kw))

	def previous(self):
		return Block(self.previousBlock)

	def transactions(self):
		return rest.GET.api.transactions(blockId=self.id, returnKey="transactions")
