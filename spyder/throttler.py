m __future__ import print_function
import sys, os
import time
sys.path.append(os.path.abspath('../'))
from defines import *
from datastore import Datastore

# Inconsistent with Datastore
def throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper

def final_throttle(method):
	def wrapper(class_obj, item, *args, **kwargs):
		if item['shutdown']:
			Datastore.factory().update("POWER_SWITCH", "KILL")
			return item
		return method(class_obj, item, *args, **kwargs)
	return wrapper
