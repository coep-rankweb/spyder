from scrapy import log
import os, sys
sys.path.append(os.path.abspath('..'))
from webclassifier import WebClassifier
import redis
from scrapy.exceptions import DropItem
from goose import Goose
import nltk
from unidecode import unidecode
import time

t = open("data/time.txt", "w")

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
		s = time.time()
		if self.r.get("%s:%s" % (self.URL_TO_ID, item['url'])):
			#duplicate
			e = time.time()
			t.write("DuplicatesFilter.process_item:found duplicate: %f\n" %  (e - s))
			raise DropItem
		else:
			#process new item
			self.buildURLIndex(item)
		e = time.time()
		t.write("DuplicatesFilter.process_item:processed new url: %f\n" % (e - s))
		return item

	def buildURLIndex(self, item):
		'''
		Assign id to current url
		Each link's url is assigned an ID and vice versa
		'''
		#url has not been processed before
		s = time.time()
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
		e = time.time()
		t.write("DuplicatesFilter.buildURLIndex:processed %d links:%f\n" % (len(set(item['link_set'])), (e - s)))


class TextExtractor(object):
	''' Extracts text from the raw_html field of the item '''
	def __init__(self):
		self.g = Goose()

	def process_item(self, item, spider):
		print item['url']
		s = time.time()
		if not item['raw_html']: item['extracted_text'] = ""
		else:
			temp = self.g.extract(raw_html = item['raw_html']).cleaned_text
			try:
				temp = unicode(temp, encoding = "UTF-8")
			except: pass
			item['extracted_text'] = unidecode(temp)
		e = time.time()
		t.write("TextExtractor.process_item: extracted textual content:%f\n" % (e - s))
		return item


class KeywordExtractor(object):
	'''
	Extracts keywords from title, extracted_text, meta_description
	'''
	def __init__(self):
		self.r = redis.Redis()
		self.URL_TO_ID = "URL2ID"
		self.WORD_SET = "WORD_SET"
		self.WORD_IN = "WORD_IN"
		self.stemmer = nltk.stem.PorterStemmer()

	def process_item(self, item, spider):
		s = time.time()

		text = item['title'] + " . " + item['extracted_text'] + " . " + item['meta_description']
		words = nltk.wordpunct_tokenize(text)
		self.buildWordIndex(words, item)
		pos = nltk.pos_tag(words)
		item['keywords'] = list(set([self.clean(x[0]) for x in pos if x[1] in ['NN', 'NNS', 'NNPS', 'NNP']]))

		e = time.time()
		t.write("KeywordExtractor.process_item:extracted keywords:%f\n" % (e - s)) 
		return item

	def buildWordIndex(self, words, item):
		'''
		Get current url id
		For each word in current url's text,
			add the url to the set of urls which contain that word
		'''
		s = time.time()
		url_id = self.r.get("%s:%s" % (self.URL_TO_ID, item['url']))
		for word in words:
			word = self.clean(word)
			self.r.sadd("%s:%s" % (self.WORD_IN, word), url_id)
			self.r.sadd(self.WORD_SET, word)
		e = time.time()
		t.write("KeywordExtractor.buildWordIndex:built word index for %d words:%f\n" % (len(words), (e - s)))

	def clean(self, s):
		return self.stemmer.stem(s.lower())



class PageClassifier(object):
	def __init__(self):
		#self.w = WebClassifier("../")
		#self.w.loadClassifier()
		pass

	def process_item(self, item, spider):
		item['proba'] = [0.2] * 15
		item['predict'] = [1]
		return item

		s = time.time()
		result = self.w.test([item['keywords']])
		item['proba'] = result['predict_proba']
		item['predict'] = result['predict']
		e = time.time()
		t.write("PageClassifier.process_item:classify page:%f\n" % (e - s))
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
		s = time.time()
		self.writeURL(item)
		self.writeKeywords(item)
		self.writeWebMatrix(item)
		self.writeClasses(item)
		e = time.time()
		t.write("DataWriter.process_item:write all files:%f\n" % (e - s))
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
