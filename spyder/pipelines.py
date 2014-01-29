# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import os, sys
sys.path.append(os.path.abspath('../'))
from webclassifier import WebClassifier
from datastore import Datastore
from scrapy.exceptions import DropItem
from goose import Goose
import nltk
from unidecode import unidecode

class DuplicatesFilter(object):
	'''
	Filters duplicate urls
	Assigns each url a unique id
	Sets url -> id and id -> url in redis
	'''
	def __init__(self):
		self.r = Datastore()
		#self.r.flushdb()
		self.URL_TO_ID = "URL2ID"
		self.URL_SET = "URL_SET"
		self.ID_TO_URL = "ID2URL"
		self.URL_CTR = "URL_CTR"
		self.r.set(self.URL_CTR, -1)

	def process_item(self, item, spider):
		if self.r.get("%s:%s" % (self.URL_TO_ID, item['url'])):
			#duplicate
			raise DropItem
		else:
			#process new item
			self.buildURLIndex(item)
		return item

	def buildURLIndex(self, item):
		'''
		Assign id to current url
		Each link's url is assigned an ID and vice versa
		'''
		#url has not been processed before
		self.r.sadd(self.URL_SET, item['url'])
		url_id = self.r.incr(self.URL_CTR, 1)
		self.r.set("%s:%d" % (self.ID_TO_URL, url_id), item['url'])
		self.r.set("%s:%s" % (self.URL_TO_ID, item['url']), url_id)

		for link in set(item['link_set']):
			if not self.r.get("%s:%s" % (self.URL_TO_ID, link)):
				new_url_id = self.incr(self.URL_CTR, 1)
				self.r.sadd(self.URL_SET, link)
				self.r.set("%s:%s" % (self.URL_TO_ID, link), new_url_id)
				self.r.set("%s:%d" % (self.ID_TO_URL, new_url_id), link)


class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''
	def __init__(self):
		self.g = Goose()

	def process_item(self, item, spider):
		print item['url']

		if not item['raw_html']:
			item['extracted_text'] = ""
		else:
			temp = nltk.clean_html(item['raw_html'])
			extract = self.g.extract(raw_html = item['raw_html'])
			if extract.meta_lang != 'en':
				raise DropItem
			#temp = extract.cleaned_text
			try:
				temp = unicode(temp, encoding = "UTF-8")
			except: pass
			item['extracted_text'] = unidecode(temp)
		return item


class KeywordExtractor(object):
	'''
	Extracts keywords from title, extracted_text, meta_description
	'''
	def __init__(self):
		self.r = Datastore()
		self.URL_TO_ID = "URL2ID"
		self.WORD_SET = "WORD_SET"
		self.WORD_TO_ID = "WORD2ID"
		self.WORD_IN = "WORD_IN"
		self.WORD_CTR = "WORD_CTR"
		self.r.set(self.WORD_CTR, -1)
		self.stemmer = nltk.stem.PorterStemmer()
		self.stopwords = set.union(set(['twitter', 'facebook', 'googl', 'youtub', 'share', 'search']), nltk.corpus.stopwords.words('english'))

	def process_item(self, item, spider):
		text = item['title'] + " . " + item['extracted_text'] + " . " + item['meta_description']
		words = nltk.wordpunct_tokenize(text)
		cleaned_words = set([x[0] for x in words]) - self.stopwords
		cleaned_words = [self.clean(w) for w in cleaned_words if w.isalnum() and len(w) > 1]
		item['words'] = cleaned_words
		self.buildWordIndex(item)

		#pos = nltk.pos_tag(words)
		#item['parts_of_speech'] = [(self.clean(x[0]), x[1]) for x in pos]

		return item

	def buildWordIndex(self, item):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word
		'''
		url_id = self.r.get("%s:%s" % (self.URL_TO_ID, item['url']))
		for word in item['words']:
			self.r.sadd("%s:%s" % (self.WORD_IN, word), url_id)
			self.r.sadd(self.WORD_SET, word)
			ctr = self.r.incr(self.WORD_CTR, 1)
			self.r.set("%s:%s" % (self.WORD_TO_ID, word), ctr)

	def clean(self, s):
		return self.stemmer.stem(s.lower())


class Stat(object):
	def __init__(self):
		self.r = Datastore()
		self.DIGRAM = "DIGRAM"
		self.OCCUR = "OCCUR"
		self.DIGRAM_SET = "DIGRAM_SET"
		self.OCCUR_SET = "OCCUR_SET"
		self.DF = "DF"

	def process_item(self, item, spider):
		item = self.markov(item)
		item = self.df(item)
		return item

	def markov(self, item):
		pos_iter = iter(item['parts_of_speech'])
		next_elem = pos_iter.next()
		while True:
			try:
				cur_elem, next_elem = next_elem, pos_iter.next()
				if cur_elem[1] in allowed and next_elem[1] in allowed:
					if cur_elem[0].isalnum() and next_elem[0].isalnum():
						self.r.incr("%s:%s:%s" % (self.DIGRAM, cur_elem[0], next_elem[0]), 1)
						self.r.incr("%s:%s" % (self.OCCUR, cur_elem[0]), 1)

						self.r.sadd(self.DIGRAM_SET, "%s:%s" % (cur_elem[0], next_elem[0]))
						self.r.sadd(self.OCCUR_SET, "%s" % cur_elem[0])
			except StopIteration:
				break
		return item


	def df(self, item):
		for k in item['words']:
			self.r.incr("%s:%s" % (self.DF, k), 1)
		return item


class PageClassifier(object):
	def __init__(self):
		self.w = WebClassifier()
		self.w.loadClassifier()

	def process_item(self, item, spider):
		result = self.w.test([item['words']])
		item['proba'] = result['predict_proba']
		item['predict'] = result['predict']
		return item

class DataWriter(object):
	def __init__(self):
		# 0 means unbuffered
		self.f_url = open("data/url.txt", "w")
		self.f_key = open("data/keywords.txt", "w")
		self.f_mat = open("data/matrix.mtx", "w")
		self.f_cla = open("data/classes.txt", "w")
		self.r = Datastore()

		self.URL_TO_ID = "URL2ID"
		self.URL_SET = "URL_SET"
		self.ID_TO_URL = "ID2URL"

		l = enumerate(os.listdir("/home/nvdia/kernel_panic/core/config_data/classes_odp"))
		l = [(x[0] + 1, x[1]) for x in l]
		self.classes = dict(l)

	def process_item(self, item, spider):
		self.writeURL(item)
		self.writeKeywords(item)
		self.writeWebMatrix(item)
		self.writeClasses(item)
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
		u = self.r.get("%s:%s" % (self.URL_TO_ID, item['url']))
		v = 0
		for link in set(item['link_set']):
			v = self.r.get("%s:%s" % (self.URL_TO_ID, link))
			self.f_mat.write("%s\t%s\t1\n" % (u, v))

	def writeClasses(self, item):
		self.f_cla.write("%s:%s\n" % (item['title'], self.classes[item['predict'][0]]))
		#self.f_cla.write("%s\n" % str(item['proba']))
