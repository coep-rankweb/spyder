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
		self.URL_CTR = "URL_CTR"
		self.URL2ID = "URL2ID"
		self.ID2URL = "ID2URL"
		self.URL_SET = "URL_SET"

	@classmethod
	def from_settings(cls, settings):
		return cls(job_dir(settings))

	def request_seen(self, request):
		#print "filter:", request.url
		uid = self.r.get("%s:%s" % (self.URL2ID, hashxx(request.url)))
		if not uid:
			uid = self.r.incr(self.URL_CTR, 1)
			self.r.set("%s:%s" % (self.ID2URL, uid), request.url)
			self.r.set("%s:%s" % (self.URL2ID, hashxx(request.url)), uid)
			self.r.sadd(self.URL_SET, uid)
		else:
			log.msg("FILTER SEEN:%s" % request.url, level = log.CRITICAL)
			return True

	def close(self, reason):
		pass
