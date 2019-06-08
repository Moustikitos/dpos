# -*- coding: utf-8 -*-
import datetime
import pytz

from collections import OrderedDict
from dposlib import rest
from dposlib.blockchain import slots


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
