from pymongo import MongoClient

client = MongoClient()

url = client.SPIDER_DB.PROC_URL_DATA

fpath = "/home/nvidia/kernel_panic/core/cusp/a_gpu"

with open(fpath) as rank_file:
	count = 1
	for rank in rank_file:
		url.update({"_id" : count}, {"$set" : {"rank": float(rank.strip())}})
		count += 1
	print count
