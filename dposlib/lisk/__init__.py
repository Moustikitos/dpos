# -*- coding: utf-8 -*-
# © Toons

import sys
import pytz

from datetime import datetime

from dposlib import rest
from dposlib.lisk import crypto
from dposlib.blockchain import cfg, slots
from dposlib.util.asynch import setInterval


DAEMON_PEERS = None

def select_peers():
	selection = []
	for seed in cfg.seeds:
		if rest.check_latency(seed):
			selection.append(seed)

	if len(selection):
		cfg.peers = selection


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	print(cfg.begintime)
	cfg.begintime = datetime(*cfg.begintime, tzinfo=pytz.UTC)
	resp = rest.GET.api.blocks.getNethash()
	if resp.get("success", False):
		cfg.headers["version"] = str(rest.GET.api.peers.version(returnKey="version"))
		cfg.headers["nethash"] = resp["nethash"]
		cfg.fees = rest.GET.api.blocks.getFees()["fees"]

		# select peers immediately and keep refreshing them in a thread so we
		# are sure we make requests to working peers
		select_peers()
		DAEMON_PEERS = rotate_peers()
	else:
		sys.stdout.write(
			("%s\n" % resp.get("error", "...")).encode("ascii", errors="replace").decode()
		)
		raise Exception("Initialization error with peer %s" % resp.get("peer", "???"))


def stop():
	global DAEMON_PEERS
	DAEMON_PEERS.set()

