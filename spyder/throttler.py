from __future__ import print_function
import sys
import time
sys.path.append(os.path.abspath('../'))
from defines import *
from datastore import Datastore

def throttle():
	def decorator(method):
		def wrapper(item, *args, **kwargs):
			if item['shutdown']:
				return item
			return method(*args, **kwargs)
		return wrapper
	return decorator

def final_throttle():
	def decorator(method):
		def wrapper(item, *args, **kwargs):
			if item['shutdown']:
				Datastore().update(CRAWLER_DATA, {'spider': 'google'}, {'POWER_SWITCH': 'kill'})
				return item
			return method(*args, **kwargs)
		return wrapper
	return decorator

