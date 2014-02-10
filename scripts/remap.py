import redis

r = redis.Redis()

with open("data/url.txt") as f:
	for index, url in enumerate(f):
		url = url.strip()
		old_id =  r.get("URL2ID:" + url)
		r.set("MAP:%s" % old_id, index + 1)
		r.set("URL2ID:%s" % url, index + 1)
		r.set("ID2URL:%d" % (index + 1), url)
		r.sadd("MAPPED", index + 1)
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
			newf.write("%s\t%s\t%s\n" % (u, v, val))
			num_edges += 1
			r.sadd("IN_LINKS:%s" % v, u)
			r.sadd("OUT_LINKS:%s" % u, v)

for i in r.smembers ("URL_SET"):
	if not r.sismember("MAPPED", i):
		r.delete("ID2URL:%s" % i)


oldf.close()
newf.close()

for word in r.smembers("WORD_SET"):
	word_id = r.get("WORD2ID:" + word)
	for u in r.smembers("WORD_IN:" + word_id):
		if r.get("MAP:" + u):
			r.sadd("FOUND_IN:" + word_id, r.get("MAP:" + u))
	r.delete("WORD_IN:" + word_id)

for i in r.smembers("MAPPED_OLD"):
	r.delete("MAP:" + i)

print "Num nodes:", r.scard("MAPPED")
print "Num edges:", num_edges



r.delete("URL_SET")
r.delete("MAPPED_OLD")
r.delete("MAPPED")
