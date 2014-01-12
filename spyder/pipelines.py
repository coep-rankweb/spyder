# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import os, sys
sys.path.append(os.path.abspath('..'))
from webclassifier import WebClassifier
import redis
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
		self.r = redis.Redis()
		self.count = 1
		#self.r.flushdb()
		self.URL_TO_ID = "URL2ID"
		self.URL_SET = "URL_SET"
		self.ID_TO_URL = "ID2URL"

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
		self.r.set("%s:%d" % (self.ID_TO_URL, self.count), item['url'])
		self.r.set("%s:%s" % (self.URL_TO_ID, item['url']), self.count)
		self.count += 1

		for link in set(item['link_set']):
			if not self.r.get("%s:%s" % (self.URL_TO_ID, link)):
				self.r.sadd(self.URL_SET, link)
				self.r.set("%s:%s" % (self.URL_TO_ID, link), self.count)
				self.r.set("%s:%d" % (self.ID_TO_URL, self.count), link)
				self.count += 1


class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''
	def __init__(self):
		self.g = Goose()

	def process_item(self, item, spider):
		print item['url']

		#item['extracted_text'] = self.g.extract(raw_html = item['raw_html']).cleaned_text
		temp = self.g.extract(raw_html = item['raw_html']).cleaned_text
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
		#grammar = "NP: {<JJ>*<NN.*>+|<NN.*>+<IN><NN.*>+}"
		#self.p = nltk.RegexpParser(grammar)
		self.r = redis.Redis()
		self.URL_TO_ID = "URL2ID"
		self.WORD_SET = "WORD_SET"
		self.WORD_IN = "WORD_IN"
		self.stemmer = nltk.stem.PorterStemmer()

	def process_item(self, item, spider):
		text = item['title'] + " . " + item['extracted_text'] + " . " + item['meta_description']
		words = nltk.wordpunct_tokenize(text)
		self.buildWordIndex(words, item)

		pos = nltk.pos_tag(words)
		item['keywords'] = list(set([x[0] for x in pos if x[1] in ['NN', 'NNS', 'NNPS', 'NNP']]))

		'''
		*** For extracting noun phrases ***

		t = self.p.parse(pos)
		subtrees = t.subtrees()
		item['keywords'] = set()
		for i in list(subtrees)[1:]:
			st = ""
			for j in i.leaves():
				st += j[0] + " "
			item['keywords'].add(st.strip())

		'''
		return item

	def buildWordIndex(self, words, item):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word
		'''
		url_id = self.r.get("%s:%s" % (self.URL_TO_ID, item['url']))
		for word in words:
			word = self.clean(word)
			self.r.sadd("%s:%s" % (self.WORD_IN, word), url_id)
			self.r.sadd(self.WORD_SET, word)

	def clean(self, s):
		return self.stemmer.stem(s.lower())



class PageClassifier(object):
	def __init__(self):
		self.w = WebClassifier()
		self.w.loadClassifier()

	def process_item(self, item, spider):
		result = self.w.test([item['keywords']])
		item['proba'] = result['predict_proba']
		item['predict'] = result['predict']
		return item

class DataWriter(object):
	def __init__(self):
		self.f_url = open("data/url.txt", "w")
		self.f_key = open("data/keywords.txt", "w")
		self.f_mat = open("data/matrix.mtx", "w")
		self.f_cla = open("data/classes.txt", "w")
		self.r = redis.Redis()

		self.URL_TO_ID = "URL2ID"
		self.URL_SET = "URL_SET"
		self.ID_TO_URL = "ID2URL"

		self.classes = {
			1: 'geography',
			2: 'science',
			3: 'society',
			4: 'history',
			5: 'finance',
			6: 'tech',
			7: 'sports',
			8: 'arts'
		}

	def process_item(self, item, spider):
		self.writeURL(item)
		self.writeKeywords(item)
		self.writeWebMatrix(item)
		self.writeClasses(item)
		return item

	def writeURL(self, item):
		self.f_url.write(item['url'] + "\n")

	def writeKeywords(self, item):
		for k in item['keywords']:
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
		self.f_cla.write("%s\n" % str(item['proba']))
