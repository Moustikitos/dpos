# -*- coding: utf-8 -*-
# © Toons
import io
import os
import re
import sys
import json
import random
import logging

from importlib import import_module
from datetime import datetime

import pytz
import requests

from dposlib import FROZEN, ROOT
from dposlib.blockchain import cfg


LOG = logging.getLogger(__name__)


def check_latency(peer):
	"""
	Returns latency in second for a given peer
	"""
	try:
		request = requests.get(peer, timeout=cfg.timeout, verify=cfg.verify)
	except Exception:
		# we want to capture all exceptions because we don't want to stop checking latency for
		# other peers that might be working
		return False
	return request.elapsed.total_seconds()


#################
#  API wrapper  #
#################

class EndPoint(object):

	@staticmethod
	def _GET(*args, **kwargs):
		# API response contains several fields and wanted one can be extracted using
		# a returnKey that match the field name
		return_key = kwargs.pop('returnKey', False)
		peer = kwargs.pop('peer', False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			data = requests.get(
				peer + "/".join(args),
				params=dict([k.replace('and_', 'AND:'), v] for k,v in kwargs.items()),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			).json()
		except Exception as error:
			data = {"success": False, "error": error, "peer": peer}
		else:
			if data.get("success") is True and return_key:
				data = data.get(return_key, {})
				if isinstance(data, dict):
					for item in ["balance", "unconfirmedBalance", "vote"]:
						if item in data:
							data[item] = float(data[item]) / 100000000
		return data

	@staticmethod
	def _POST(*args, **kwargs):
		peer = kwargs.pop("peer", False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			data = requests.post(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			).json()
		except Exception as error:
			data = {"success": False, "error": error, "peer": peer}
		return data

	@staticmethod
	def _PUT(*args, **kwargs):
		peer = kwargs.pop("peer", False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			data = requests.put(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			).json()
		except Exception as error:
			data = {"success": False, "error": error, "peer": peer}
		return data

	def __init__(self, elem=None, parent=None, method=None):
		if method not in [EndPoint._GET, EndPoint._POST, EndPoint._PUT]:
			raise Exception("REST method is not a valid one")
		self.elem = elem
		self.parent = parent
		self.method = method

	def __getattr__(self, attr):
		if attr not in ["elem", "parent", "method", "chain"]:
			if re.match("^_[0-9A-Fa-f].*", attr):
				attr = attr[1:]
			return EndPoint(attr, self, self.method)
		else:
			return object.__getattr__(self, attr)

	def __call__(self, **kwargs):
		return self.method(*self.chain(), **kwargs)

	def chain(self):
		return (self.parent.chain() + [self.elem]) if self.parent!=None else [""]

GET = EndPoint(method=EndPoint._GET)
POST = EndPoint(method=EndPoint._POST)
PUT = EndPoint(method=EndPoint._PUT)


#######################
#  network selection  #
#######################

def load(family_name):
	"""
	Loads a given blockchain package as `dposlib.core`
	"""
	# initialize blockchain familly package
	# try:
	sys.modules[__package__].core = import_module('dposlib.{0}'.format(family_name))
	sys.modules[__package__].core.init()
	# except:
	# 	raise Exception("%s is in readonly mode (no crypto package found)" % family_name)

	# delete real package name loaded to keep namespace clear
	try:
		sys.modules[__package__].__delattr__(family_name)
	except AttributeError:
		pass


def use(network, **kwargs):
	"""
	Sets the blockchain parameters in the `cfg` module and initialize blockchain
	package.
	"""
	# clear data in cfg module and initialize with minimum vars
	cfg.__dict__.clear()
	cfg.network = None
	cfg.hotmode = False
	
	path = os.path.join(ROOT, "network", network + ".net")
	if os.path.exists(path):
		with io.open(os.path.join(ROOT, "network", network + ".net")) as f:
			data = json.load(f)
	else:
		raise Exception('"{}" blockchain parameters does not exist'.format(network))
	data.update(**kwargs)
	cfg.__dict__.update(data)
	cfg.verify = os.path.join(os.path.dirname(sys.executable), 'cacert.pem') if FROZEN else True
	cfg.begintime = datetime(*cfg.begintime, tzinfo=pytz.UTC)

	if data.get("seeds", False):
		cfg.peers = []
		for seed in cfg.seeds:
			if check_latency(seed):
				cfg.peers.append(seed)
				del cfg.seeds
				break
	else:
		for peer in data.get("peers", []):
			peer = "http://{0}:{1}".format(peer, data.get("port", 22))
			if check_latency(peer):
				cfg.peers = [peer]
				break

	if len(cfg.peers):
		try:
			load(cfg.familly)
		except Exception as e:
			cfg.hotmode = False
			sys.stdout.write("%s\n" % e)
		else:
			cfg.hotmode = True
		finally:
			cfg.network = network
	else:
		raise Exception("Error occurred during network setting...")
