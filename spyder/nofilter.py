from scrapy.utils.job import job_dir
from scrapy.dupefilter import BaseDupeFilter

class Nofilter(BaseDupeFilter):
	"""Request Fingerprint duplicates filter"""

	def __init__(self, path=None):
		self.file = None
		self.fingerprints = None

	@classmethod
	def from_settings(cls, settings):
		return cls(job_dir(settings))

	def request_seen(self, request):
		pass

	def close(self, reason):
		self.fingerprints = None
