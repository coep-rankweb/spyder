from scrapy import log
import os, sys
sys.path.append(os.path.abspath('../'))
#from webclassifier import WebClassifier
from datastore import Datastore
from scrapy.exceptions import DropItem
import nltk
from unidecode import unidecode
from timer import timeit
from pyhashxx import hashxx
import psutil


class DuplicatesFilter(object):
	'''
	Filters duplicate urls
	Assigns each url a unique id
	Sets url -> id and id -> url in redis
	Indexes inlinks and outlinks
	'''
	def __init__(self):
		self.r = Datastore()
		self.URL2ID = "URL2ID"
		self.MEM_THRESHOLD = 10 * (10 ** 9)
		self.redis_process = None
		self.scrapy_process = None

		for i in psutil.process_iter():
			if i.name.find("redis-server") >= 0:
				self.redis_process = i
			if i.name.find("scrapy") >= 0:
				self.scrapy_process = i

	def process_item(self, item, spider):
		if not item:
			raise DropItem

		if self.redis_process.get_memory_info().rss + self.scrapy_process.get_memory_info().rss > self.MEM_THRESHOLD:
			self.r.set("POWER_SWITCH", "OFF")
			item['shutdown'] = True

		if item['shutdown']:
			return item

		if not item['link_set']:
			raise DropItem
		else:
			self.buildURLIndex(item)
		return item

	def buildURLIndex(self, item):

		hashed_url = hashxx(item['url'])
		url_id = self.r.get("%s:%s" % (self.URL2ID, hashed_url))

		assert url_id != None

		item['url_id'] = -1 * int(url_id)

class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''
	def __init__(self):
		self.adult_blacklist = ['sex', 'porn', 'xxx', 'fuck', 'nude']
		pass

	def process_item(self, item, spider):
		if item['shutdown']:
			return item

		if not item['raw_html']:
			item['extracted_text'] = ""
		else:
			temp = nltk.clean_html(item['raw_html'])
			try:
				temp = unicode(temp, encoding = "UTF-8")
			except: pass
			item['extracted_text'] = unidecode(temp)

		lower_extracted_text = item['extracted_text'].lower()
		for b in self.adult_blacklist:
			if b in lower_extracted_text:
				raise DropItem
		return item


class KeywordExtractor(object):
	'''
	Extracts keywords from title, extracted_text, meta_description
	'''
	def __init__(self):
		self.r = Datastore()
		self.URL2ID = "URL2ID"
		self.WORD_SET = "WORD_SET"
		self.WORD2ID = "WORD2ID"
		self.WORD_IN = "WORD_IN"
		self.WORD_CTR = "WORD_CTR"
		#self.r.set(self.WORD_CTR, -1)
		self.stemmer = nltk.stem.PorterStemmer()
		self.stopwords = set([self.clean(x) for x in nltk.corpus.stopwords.words('english')])

	def process_item(self, item, spider):
		if item['shutdown']:
			return item

		text = item['title'] + " . " + item['extracted_text'] + " . " + item['meta_description']
		words = [self.clean(x) for x in nltk.wordpunct_tokenize(text)]
		item['ordered_words'] = words
		cleaned_words = set(words) - self.stopwords
		cleaned_words = [self.clean(w) for w in cleaned_words if w.isalnum() and len(w) > 1 and not w.isdigit()]
		item['words'] = cleaned_words
		if not item['words']:
			raise DropItem

		self.buildWordIndex(item)

		return item

	def buildWordIndex(self, item):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word
		'''
		url_id = item['url_id']
		#url_id = self.r.get("%s:%s" % (self.URL2ID, hashxx(item['url'])))
		word_id = ""
		for word in item['words']:
			if self.r.sadd(self.WORD_SET, word):
				word_id = str(self.r.incr(self.WORD_CTR, 1))
				self.r.set("%s:%s" % (self.WORD2ID, word), word_id)
			else:
				word_id = self.r.get("%s:%s" % (self.WORD2ID, word))
			self.r.sadd("%s:%s" % (self.WORD_IN, word_id), url_id)

	def clean(self, s):
		return self.stemmer.stem(s.lower())


class Analytics(object):
	def __init__(self):
		self.r = Datastore()
		self.DIGRAM = "DIGRAM"
		self.WORD2ID = "WORD2ID"
		self.TOP_N = 5
		self.bgm = nltk.collocations.BigramAssocMeasures
		self.SCORER_FN = self.bgm.likelihood_ratio

	def process_item(self, item, spider):
		if item['shutdown']:
			return item

		item = self.markov(item)
		return item

	def markov(self, item):
		finder = nltk.collocations.BigramCollocationFinder.from_words(item['ordered_words'])
		digrams = finder.nbest(self.SCORER_FN, self.TOP_N)

		for digram in digrams:
			w0 = self.r.get("%s:%s" % (self.WORD2ID, digram[0]))
			w1 = self.r.get("%s:%s" % (self.WORD2ID, digram[1]))
			self.r.incr("%s:%s:%s" % (self.DIGRAM, w0, w1), 1)
		return item


class PageClassifier(object):
	def __init__(self):
		self.w = WebClassifier()
		self.w.loadClassifier()

	def process_item(self, item, spider):
		if item['shutdown']:
			return item

		result = self.w.test([item['words']])
		item['proba'] = result['predict_proba']
		item['predict'] = result['predict']
		return item

class DataWriter(object):
	def __init__(self):
		self.f_url = open("data/url.txt", "a+")
		self.f_key = open("data/keywords.txt", "a+")
		self.f_mat = open("data/matrix.mtx", "a+")
		self.f_cla = open("data/classes.txt", "a+")
		self.r = Datastore()

		self.URL_SET = "URL_SET"
		self.URL2ID = "URL2ID"
		self.ID2URL = "ID2URL"
		self.PROCESSED_CTR = "PROCESSED_CTR"

		'''l = enumerate(os.listdir("/home/nvdia/kernel_panic/core/config_data/classes_odp"))
		l = [(x[0] + 1, x[1]) for x in l]
		self.classes = dict(l)'''

	def process_item(self, item, spider):
		if item['shutdown']:
			self.f_url.close()
			self.f_key.close()
			self.f_mat.close()
			self.f_cla.close()
			self.r.set("POWER_SWITCH", "KILL")
			#print >>sys.stderr, "KILLED"
			return item

		self.writeURL(item)
		self.writeKeywords(item)
		self.writeWebMatrix(item)
		#self.writeClasses(item)

		url_id = item['url_id']
		self.r.srem(self.URL_SET, -1 * url_id)
		self.r.sadd(self.URL_SET, url_id)
		self.r.incr(self.PROCESSED_CTR, 1)
		print item['url']

		return item

	def writeURL(self, item):
		self.f_url.write(item['url'] + "\n")

	def writeKeywords(self, item):
		for k in item['words']:
			self.f_key.write("%s," % k)
		self.f_key.write("\n")

	def writeWebMatrix(self, item):
		'''
		Builds web graph in matrix market format file
		'''
		u = hashxx(item['url'])
		v = 0
		for link in set(item['link_set']):
			v = hashxx(link)
			self.f_mat.write("%s\t%s\t1\n" % (u, v))

	def writeClasses(self, item):
		self.f_cla.write("%s:%s\n" % (item['title'], self.classes[item['predict'][0]]))
		#self.f_cla.write("%s\n" % str(item['proba']))
