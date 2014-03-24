from pymongo import MongoClient
import sys
import itertools

client = MongoClient()

url = client['SPIDER_DB']['URL_DATA']
nurl = client['SPIDER_DB']['PROC_URL_DATA']

url.remove({'out_links' : {'$exists':False}})

count = 1
for entry in url.find():
	print url.update(entry, {'$set' : {'mtx_index':count}}), count
	count += 1

print "built mtx_index"

url.create_index('mtx_index')
count = 1
with open("data/web.mtx", "w") as web:
	web.write("\n\n\n")
	rows = url.find().sort('mtx_index')
	for row in rows:
		u = row['mtx_index']
		for col in row['out_links']:
			try:
				v = url.find_one({'_id':col})['mtx_index']
				web.write("%s\t%s\t1\n" % (u, v))
			except TypeError:
				pass
		count += 1
		if count % 1000 == 0: print count

print "built web.mtx"


old_u = None
with open("data/web.mtx") as web:
	web.next()
	web.next()
	web.next()
	while True:
		try:
			i = web.next()
			u, v, w = map(int, i.strip().split())

			if not old_u:
				old_u = u
				out_links = set()
				newobj = url.find_one({'mtx_index':u})
				newobj['_id'] = newobj['mtx_index']
				del newobj['mtx_index']

			if old_u == u:
				out_links.add(v)
			else:
				print old_u
				newobj['out_links'] = list(out_links)
				nurl.insert(newobj)
				web = itertools.chain([i], web)
				old_u = None

		except StopIteration:
			print old_u
			newobj['out_links'] = list(out_links)
			nurl.insert(newobj)
			break

print "built PROC_URL_DATA"

word = client['SPIDER_DB']['WORD_DATA']
nword = client['SPIDER_DB']['PROC_WORD_DATA']

d = {}	# maps old _id to new _id (mtx_index)
in_list = ['in_url', 'in_body', 'in_title']
for entry in word.find():
	set_dict = { key: set() for key in in_list }
	print entry['word']

	for s in in_list:
		try:
			for u in entry[s]:
				if u in d:
					url_id = d[u]
				else:
					url_id = url.find_one({"_id" : u})['mtx_index']
			
				set_dict[s].add(url_id)
		except KeyError:
			pass

	newobj = entry
	for s in in_list:
		newobj[s] = list(set_dict[s])

	nword.insert(newobj)
