# -*- coding: utf-8 -*-
# © Toons

import os
import io
import json

from dposlib import PY3


def loadJson(path):
	"""Load JSON data from path"""
	if os.path.exists(path):
		with io.open(path, encoding="utf-8") as in_:
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
	with io.open(
		path, 
		"w" if PY3 else "wb", 
		**({"encoding":"utf-8"} if PY3 else {})
	) as out:
		json.dump(data, out, indent=4)


def filter_dic(dic):
	special_keys = [
		"amount",
		"balance",
		"fee", "fees", "forged",
		"reward", "rewards",
		"totalAmount", "totalFee", "totalForged", "total",
		"unconfirmedBalance",
		"votes"
	]

	def cast_value(typ, value):
		try:
			return typ(value)/100000000.0
		except:
			return filter_dic(value) if isinstance(value, dict) else value

	return dict(
		(k,
			cast_value(float, v) if k in special_keys else \
			filter_dic(v) if isinstance(v, dict) else \
			v
		) for k,v in dic.items()
	)
