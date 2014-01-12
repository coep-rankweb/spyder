crawl:
	python reset.py
	rm -f *.[mt]x[t] *.pyc
	scrapy crawl google
