# -*- coding: utf-8 -*-
import datetime
import pytz

from collections import OrderedDict
from dposlib import rest
from dposlib.blockchain import slots


class DataIterator:

	def __init__(self, endpoint, tries=10):
		if not isinstance(endpoint, rest.EndPoint):
			raise Exception("Invalid endpoint class")
		self.endpoint = endpoint
		self.data = {}
		self.page = 0
		self.errors = 0
		self.tries = tries

	def __next__(self):
		if not self.data.get("meta", {}).get("next", None) and self.page:
			raise StopIteration("End of data reached")
		else:
			self.page += 1
			data = self.endpoint(page=self.page)
			if not data.get("error", False):
				self.errors += 1
				self.data = data
		return self.data.get("data", [])

	def __iter__(self):
		while True:
			try:
				yield next(self)
			except:
				break
			else:
				if self.errors > self.tries:
					raise Exception("Too much unsuccesfull tries")


def loadPages(endpoint, pages=False, nb_tries=10, limit=False):
	data_iterator = DataIterator(endpoint, nb_tries)
	data = []
	while True:
		try:
			if limit and len(data) > limit:
				break
			_data = next(data_iterator)
		except StopIteration:
			break
		else:
			if not pages or data_iterator.page <= pages:
				data.extend(_data)
			else:
				break
				
	return data[:limit]
	# return data


def deltas():
	delegates = loadPages(rest.GET.api.delegates)
	blocks = [d["blocks"] for d in delegates]
	produced = sum(b["produced"] for b in blocks)

	last_block_timestamp = slots.getRealTime(delegates[0]["blocks"]["last"]["timestamp"]["epoch"])
	total_elapsed_time = (last_block_timestamp - rest.cfg.begintime).total_seconds()

	theorical_height = int((datetime.datetime.now(pytz.UTC) - rest.cfg.begintime).total_seconds() / rest.cfg.blocktime)

	return OrderedDict({
		"real blocktime": total_elapsed_time / produced,
		"block produced (real height)": produced,
		"theorical height": theorical_height,
		"height shift": produced - theorical_height,
	})
