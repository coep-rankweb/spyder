from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from spyder.items import WebItem
from scrapy.exceptions import CloseSpider
from unidecode import unidecode
from scrapy import log
from urlparse import urljoin, urlparse
import sys, os
sys.path.extend(["../", "spyder/"])
from defines import *
import traceback
from pymongo import MongoClient

class GoogleSpider(CrawlSpider):
	name = "google"
	allowed_domains = []

	#start_urls = ['http://www.foodnetwork.com/recipes/emeril-lagasse/cajun-jambalaya-recipe2.html', 'http://thebrowser.com/', 'http://www.popphoto.com/', 'http://www.technologyreview.com/', 'http://www.goldmansachs.com/index.html?view=desktop', 'http://www.nationalgeographic.com/', "http://www.nobelprize.org/nobel_prizes/physics/laureates/1921/einstein-bio.html"]

	start_urls = ["http://edition.cnn.com"]

	rules = (
		Rule(SgmlLinkExtractor(allow = (".*", ), allow_domains = "cnn.com"), callback = 'process', follow = True),
	)

	MU = os.environ.get("MONGOHQ_URL")
	r = MongoClient(MU)
	if MU: db = r[urlparse(MU).path[1:]]
	else: db = r[DB_NAME]
	c = db[CRAWLER_DATA]

	def process(self, response):
		status = self.c.find_one({'spider': 'google'})['POWER_SWITCH']
		item = WebItem()
		if status == "KILL":
			raise CloseSpider("shutdown")
		elif status == 'ON':
			try:
				sel = Selector(response)

				item['shutdown'] = False

				name = sel.xpath("//title/text()").extract()
				if name: item['title'] = self.clean(name[0])
				else: item['title'] = ""

				item['url'] = response.url
				item['raw_html'] = response.body

				meta = sel.xpath('//meta[@name="description"]/@content').extract()
				if meta: meta = self.clean(meta[0])
				else: meta = ""
				item['meta_description'] = meta

				abs_links = []
				rel_links = sel.xpath('//a/@href').extract()
				for l in rel_links:
					link = urljoin(response.url, l)
					if urlparse(link).scheme in ['http', 'https'] and len(link) < 512:
						abs_links.append(link)
				item['link_set'] = set(abs_links)

				return item
			except (KeyError, IndexError, TypeError, ValueError, IOError) as e:
				traceback.print_exc()
		elif status == "OFF":
			item['shutdown'] = True
			return item
		else:
			raise CloseSpider("Invalid power switch value")

	def clean(self, s):
		s = self.encode_str(s)
		s = s.strip()
		s = s.replace('\n', ' ').replace('|', ' - ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
		return s

	def encode_str(self, s):
		temp = s
		try:
			temp = unicode(temp, encoding = "UTF-8")
		except TypeError:
			pass
		return unidecode(temp)
