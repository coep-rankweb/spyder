FLAGS = -s JOBDIR=data/google_spider

reset:
	python -c "import control; control.reset()"

crawl:
	rm -rf data/*
	rm -f *.[mt]x[t] spyder/*.pyc
	scrapy crawl google $(FLAGS) 2>> data/timelog
	bash scripts/web.sh

on:
	python -c "import control; control.on()"

off:
	python -c "import control; control.off()"
