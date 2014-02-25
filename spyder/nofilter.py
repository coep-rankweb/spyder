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
		self.URL2ID = "URL2ID"

	@classmethod
	def from_settings(cls, settings):
		return cls(job_dir(settings))

	def request_seen(self, request):
		#print "filter:", request.url
		uid = self.r.get("%s:%s" % (self.URL2ID, hashxx(request.url)))
		if not uid or int(uid) > 0:
			pass
		else:
			log.msg("FILTER SEEN:%s" % request.url, level = log.CRITICAL)
			return True

	def close(self, reason):
		pass
