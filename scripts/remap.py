from pymongo import MongoClient
import itertools

client = MongoClient()

url = client['SPIDER_DB']['URL_DATA']
nurl = client['SPIDER_DB']['PROC_URL_DATA']

url.remove({'out_links':{'$exists':False}})

count = 1
for entry in url.find():
	url.update(entry, {'$set':{'mtx_index':count}})
	count += 1

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
				newobj['out_links'] = list(out_links)
				nurl.insert(newobj)
				web = itertools.chain([i], web)
				old_u = None

		except StopIteration:
			break

