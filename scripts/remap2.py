import redis
from pyhashxx import hashxx

r = redis.Redis()

new_index = 1
for i in r.smembers("URL_SET"):
	url_id = int(i)

	if i > 0:
		url = r.get("ID2URL:%s" % url_id)
		# No need to remove 'i' explicitly. In the end, we are deleting the URL_SET anyway 
		r.srem("URL_SET", i)
	else:
		url = r.get("ID2URL:%s" % (-1 * url_id))
		r.set("N:URL2ID:%s" % hashxx(url), new_index)
		r.set("N:ID2URL:%s" % new_index, url)
		new_index += 1

	r.delete("URL2ID:%s" % hashxx(url))
	r.delete("ID2URL:%s" % url_id)

print "Mapped..."
oldf = open ("data/matrix.mtx")
newf = open ("data/web.mtx", "w")
newf.write("%%MatrixMarket matrix coordinate real general\n%\n\n")

num_edges = 0
for i, line in enumerate(oldf):
	if i % 10000 == 0:
		print "Matrix file:", i
	row, col, val = line.strip().split()
	u = r.get("N:URL2ID:" + row)
	if u:
		v = r.get("N:URL2ID:" + col)
		if v:
			newf.write("%s\t%s\t%s\n" % (u, v, val))
			num_edges += 1
			r.sadd("IN_LINKS:%s" % v, u)
			r.sadd("OUT_LINKS:%s" % u, v)

print "done creating web.mtx"

oldf.close()
newf.close()

'''
There is no need to check if the url present in WORD_IN is processed.
KeywordExtractor add the urls in the WORD_IN set.
This implies that the url has to be processed.

for word in r.smembers("WORD_SET"):
	word_id = r.get("WORD2ID:" + word)

	for u in r.smembers("WORD_IN:%s" % word_id):
		uid = r.get("N:ID2URL:%s" % u)
		if not uid: r.srem("WORD_IN:%s" % word_id, u)
'''
print "Num nodes:", new_index - 1
print "Num edges:", num_edges

r.delete("URL_SET")
