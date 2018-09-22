# -*- coding: utf-8 -*-
# © Toons

import os
import io
import json

from dposlib import PY3


def loadJson(path):
	"""Load JSON data from path"""
	if os.path.exists(path):
		with io.open(path) as in_:
			data = json.load(in_)
	else:
		data = {}
	return data


def dumpJson(data, path):
	"""Dump JSON data to path"""
	try:
		os.makedirs(os.path.dirname(path))
	except:
		pass
	with io.open(path, "w" if PY3 else "wb") as out:
		json.dump(data, out, indent=4)


def filter_dic(dic):
	return dict(
		(k, float(v)/100000000 if k in [
			"amount",
			"balance",
			"fee", "fees", "forged",
			"reward", "rewards",
			"totalAmount", "totalFee", "totalForged",
			"unconfirmedBalance",
			"vote"
		] else v) for k,v in dic.items()
	)
