# -*- coding: utf-8 -*-
# © Toons

import os
import struct
import datetime
from collections import OrderedDict

import pytz
from dposlib import rest
from dposlib.blockchain import slots


class DataIterator:

	def __init__(self, endpoint, returnKey, **kwargs):
		if not isinstance(endpoint, rest.EndPoint):
			raise Exception("Invalid endpoint class")
		self.tries = kwargs.pop("tries", 10)
		self.limit = kwargs.pop("limit", 50)
		self.returnKey = returnKey
		self.endpoint = endpoint
		self.kwargs = kwargs
		self.data = {}
		self.count = 0
		self.errors = 0

	def __next__(self):
		result = []
		if not len(self.data.get(self.returnKey, [])) and self.count:
			raise StopIteration("End of data reached")
		else:
			self.data = self.endpoint(offset=self.count, limit=self.limit, **self.kwargs)
			if self.data.get("error", False) or self.returnKey not in self.data:
				self.errors += 1
			else:
				result = self.data.get(self.returnKey, [])
				self.count += len(result)
		return result

	def __iter__(self):
		while True:
			try:
				yield next(self)
			except:
				break
			else:
				if self.errors > self.tries:
					raise Exception("Too much unsuccesfull tries")


def loadPages(endpoint, returnKey, pages=False, nb_tries=10, limit=False, **kw):
	data_iterator = DataIterator(endpoint, returnKey, tries=nb_tries, **kw)
	data = []
	while True:
		try:
			if limit and len(data) > limit:
				break
			_data = next(data_iterator)
		except StopIteration:
			break
		else:
			if not pages or float(data_iterator.count)/data_iterator.limit <= pages:
				data.extend(_data)
			else:
				break
	
	if limit:
		return data[:limit]
	else:
		return data


def deltas():
	delegates = loadPages(rest.GET.api.delegates, "delegates")
	blocks = [d["producedblocks"] for d in delegates]
	produced = sum(blocks)

	last_block_timestamp = slots.getRealTime(rest.GET.api.blocks(returnKey="blocks")[0]["timestamp"])
	total_elapsed_time = (last_block_timestamp - rest.cfg.begintime).total_seconds()

	theorical_height = int((datetime.datetime.now(pytz.UTC) - rest.cfg.begintime).total_seconds() / rest.cfg.blocktime)

	return OrderedDict({
		"real blocktime": total_elapsed_time / produced,
		"block produced (real height)": produced,
		"theorical height": theorical_height,
		"height shift": produced - theorical_height,
	})
