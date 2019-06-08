# -*- coding: utf-8 -*-
# © Toons

import dposlib
from dposlib.util.data import filter_dic

class Wallet(dposlib.blockchain.Wallet):

	def __init__(self, address, **kw):
		dposlib.blockchain.Data.__init__(self, dposlib.rest.GET.api.accounts, **dict({"address":address, "returnKey":"data"}, **kw))
