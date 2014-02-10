from __future__ import print_function
import sys
import time

def timeit(argument):
	def decorator(method):
		def wrapper(*args, **kw):
			ts = time.time()
			result = method(*args, **kw)
			te = time.time()
			print('%s: %5.10f sec' % (argument, te-ts), end = "\n", file = open("timelog", "a"))
			return result
		return wrapper
	return decorator
