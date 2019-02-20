# -*- coding: utf-8 -*-
import datetime
import pytz

from dposlib import rest
from dposlib.blockchain import slots


def loadPages(endpoint, pages=None, quiet=True, nb_tries=10, limit=False):
	if not isinstance(endpoint, rest.EndPoint):
		raise Exception("Invalid endpoint class")
	count, pageCount, data = 0, 1, []
	while count < pageCount:
		req = endpoint.__call__(page=count+1)
		if req.get("error", False):
			nb_tries -= 1
			if not quiet:
				zen.logMsg("Api error occured... [%d tries left]" % nb_tries)
			if nb_tries <= 0:
				raise Exception("Api error occured: %r" % req)
		else:
			pageCount = req["meta"]["pageCount"]
			if isinstance(pages, int):
				pageCount = min(pages, pageCount)
			if not quiet:
				zen.logMsg("reading page %s over %s" % (count+1, pageCount))
			data.extend(req.get("data", []))
			count += 1
		if limit and limit < len(data):
			break
	return data


def deltas():
	delegates = loadPages(rest.GET.api.v2.delegates)
	blocks = [d["blocks"] for d in delegates]
	produced = sum(b["produced"] for b in blocks)
	missed = sum(b["missed"] for b in blocks)

	last_block_timestamp = slots.getRealTime(delegates[0]["blocks"]["last"]["timestamp"]["epoch"])
	total_elapsed_time = (last_block_timestamp - rest.cfg.begintime).total_seconds()
	total_blocks = produced + missed

	theorical_height = int((datetime.datetime.now(pytz.UTC) - rest.cfg.begintime).total_seconds() / rest.cfg.blocktime)

	return {
		"real blocktime": total_elapsed_time / produced,
		"failureless blocktime": total_elapsed_time / total_blocks,
		"block missed": missed,
		"block produced (real height)": produced,
		"theorical height": theorical_height,
		"height shift": produced - theorical_height,
		"failureless height shift": produced + missed - theorical_height
	}
