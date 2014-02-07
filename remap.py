import redis

r = redis.Redis()

with open("data/url.txt") as f:
	for index, url in enumerate(f):
		url = url.strip()
		old_id =  r.get("URL2ID:" + url)
		r.set("MAP:%s" % old_id, index)
		r.set("URL2ID:%s" % url, index)
		r.set("ID2URL:%d" % index, url)
		r.sadd("MAPPED", index)
		r.sadd("MAPPED_OLD", old_id)

oldf = open ("data/matrix.mtx")
newf = open ("data/web.mtx", "w")
newf.write("%%MatrixMarket matrix coordinate real general\n%\n\n")

num_edges = 0
for line in oldf:
	row, col, val = line.strip().split()
	u = r.get("MAP:" + row)
	if u:
		v = r.get("MAP:" + col)
		if v:
			u = int(u) + 1
			v = int(v) + 1
			newf.write("%d\t%d\t%s\n" % (u, v, val))
			num_edges += 1
			r.sadd("IN_LINKS:%d" % v, u)
			r.sadd("OUT_LINKS:%d" % u, v)

for i in r.smembers ("URL_SET"):
	if not r.sismember("MAPPED", i):
		r.delete("ID2URL:%s" % i)


oldf.close()
newf.close()

for word in r.smembers("WORD_SET"):
	word_id = r.get("WORD2ID:" + word)
	for u in r.smembers("WORD_IN:" + word_id):
		if r.get("MAP:" + u):
			r.sadd("FOUND_IN:" + word_id, u)
	r.delete("WORD_IN:" + word_id)

for i in r.smembers("MAPPED_OLD"):
	r.delete("MAP:" + i)

r.delete("URL_SET")
r.delete("MAPPED_OLD")
r.delete("MAPPED")

print num_edges
