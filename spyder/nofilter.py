from scrapy import log
import os, sys
sys.path.append(os.path.abspath('../'))
from datastore import Datastore
from scrapy.utils.job import job_dir
from scrapy.dupefilter import BaseDupeFilter
from pyhashxx import hashxx

class NoFilter(BaseDupeFilter):
	"""Request Fingerprint duplicates filter"""

	def __init__(self, path=None):
		self.r = Datastore()
		self.URL_SET = "URL_SET"

	@classmethod
	def from_settings(cls, settings):
		return cls(job_dir(settings))

	def request_seen(self, request):
		if self.r.sadd(self.URL_SET, hashxx(request.url)) == 1:
			return None
		else:
			log.msg("FILTER SEEN:%s" % request.url, level = log.CRITICAL)
			return True

	def close(self, reason):
		pass
