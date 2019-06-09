# -*- coding: utf-8 -*-
# © Toons

# ~ https://lisk.io/documentation/lisk-core/user-guide/api/0-9

import dposlib
from dposlib.util.data import filter_dic

class Wallet(dposlib.blockchain.Wallet):

	def __init__(self, address, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.accounts, **dict({"address":address, "returnKey":"account"}, **kw))
