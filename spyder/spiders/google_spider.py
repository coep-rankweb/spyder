from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from spyder.items import WebItem
from scrapy.exceptions import CloseSpider
from unidecode import unidecode
from scrapy import log
from urlparse import urljoin
import sys
sys.path.append("../")
from datastore import Datastore
import traceback

class GoogleSpider(CrawlSpider):
	name = "google"
	allowed_domains = []

	#start_urls = ["http://www.nobelprize.org/nobel_prizes/physics/laureates/1921/einstein-bio.html"]
	#start_urls = ["http://en.wikipedia.org/wiki/Bill_Gates"]
	#start_urls = ["http://www.moreintelligentlife.com/"]
	#start_urls = ["http://espn.go.com/", "http://www.moreintelligentlife.com/", "http://www.nature.com/browse/index.html", "http://edition.cnn.com/", "http://www.si.edu/", "http://www.amazon.com/"]
	start_urls = ["http://www.food.com/", "http://frenchfood.about.com/", "http://www.stanford.edu/", "http://www.paleoportal.org/"]

	rules = (
		Rule(SgmlLinkExtractor(allow = (".*", )), callback = 'process', follow = True),
	)

	r = Datastore()

	def process(self, response):
		if self.r.get("POWER_SWITCH") == 'ON':
			try:
				sel = Selector(response)
				item = WebItem()
				name = sel.xpath("//title/text()").extract()
				if name: item['title'] = self.clean(name[0])
				else: item['title'] = ""
				item['url'] = response.url
				item['raw_html'] = response.body
				rel_links = sel.xpath('//a/@href').extract()
				meta = sel.xpath('//meta[@name="description"]/@content').extract()
				if meta: meta = self.clean(meta[0])
				else: meta = ""
				item['meta_description'] = meta
				abs_links = []
				for l in rel_links:
					link = urljoin(response.url, l)
					if urlparse(link).scheme in ['http', 'https']:
						abs_links.append(link)
				item['link_set'] = abs_links
				return item
			except Exception:
				traceback.print_exc()
		else:
			raise CloseSpider("Shutdown")

	def clean(self, s):
		s = self.encode_str(s)
		s = s.strip()
		s = s.replace('\n', ' ').replace('|', ' - ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
		return s

	def encode_str(self, s):
		temp = s
		try:
			temp = unicode(temp, encoding = "UTF-8")
		except:
			pass
		return unidecode(temp)
