from scrapy import log
import os, sys
sys.path.append(os.path.abspath('../'))
from scrapy.utils.job import job_dir
import redis
from scrapy.dupefilter import BaseDupeFilter
from pyhashxx import hashxx

class DupeFilter(BaseDupeFilter):
	"""Request Fingerprint duplicates filter"""

	def __init__(self, path=None):
		self.r = redis.Redis()
		self.SEEN = "SEEN"

	@classmethod
	def from_settings(cls, settings):
		return cls(job_dir(settings))

	def request_seen(self, request):
		url = request.url.split("?")[0]
		if self.r.exists("%s:%s" % (self.SEEN, url)):
			return True
		else:
			self.r.set("%s:%s" % (self.SEEN, url), 1)
			return None

	def close(self, reason):
		pass
