# -*- coding: utf-8 -*-
# © Toons

import logging

from dposlib import rest
from dposlib.ark import crypto
from dposlib.blockchain import cfg, slots
from dposlib.util.asynch import setInterval

log = logging.getLogger(__name__)
DAEMON_PEERS = None


def select_peers():
	version = rest.GET.api.peers.version(returnKey='version') or '0.0.0'
	height = rest.GET.api.blocks.getHeight(returnKey='height') or 0
	if isinstance(height, dict) or isinstance(version, dict):
		return

	peers = rest.GET.peer.list().get('peers', [])
	good_peers = []
	for peer in peers:
		if (
			peer.get("delay", 6000) <= cfg.timeout * 1000 and peer.get("version") == version and
			peer.get("height", -1) > height - 10
		):
			good_peers.append(peer)

	good_peers = sorted(good_peers, key=lambda e: e["delay"])

	min_selection = getattr(cfg, "broadcast", 0)
	selection = []
	for peer in good_peers:
		peer = "http://{ip}:{port}".format(**peer)
		if rest.check_latency(peer):
			selection.append(peer)

		if len(selection) >= min_selection:
			break

	if len(selection) < min_selection:
		log.debug(
			'Broadcast is set to "%s", but managed to get %s peers out of %s.',
			min_selection, len(selection), len(peers)
		)

	if len(selection) >= min_selection:
		cfg.peers = selection


@setInterval(30)
def rotate_peers():
	select_peers()


def init():
	global DAEMON_PEERS
	response = rest.GET.api.loader.autoconfigure()
	if response["success"]:
		network = response["network"]
		if "version" not in cfg.headers:
			cfg.headers["version"] = str(network.pop('version'))
		cfg.headers["nethash"] = network.pop('nethash')
		cfg.__dict__.update(network)
		cfg.fees = rest.GET.api.blocks.getFees()["fees"]
		# select peers immediately and keep refreshing them in a thread so we
		# are sure we make requests to working peers
		select_peers()
		DAEMON_PEERS = rotate_peers()
	else:
		log.error(response.get('error', '...'))
		raise Exception("Initialization error with peer %s" % response.get("peer", "???"))


def stop():
	global DAEMON_PEERS
	DAEMON_PEERS.set()
