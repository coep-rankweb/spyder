# Scrapy settings for sample project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'spyder'

SPIDER_MODULES = ['spyder.spiders']
NEWSPIDER_MODULE = 'spyder.spiders'
CONCURRENT_REQUESTS = 100

LOG_LEVEL = 'ERROR'
LOG_FILE = 'data/log.txt'

DEPTH_LEVEL = 3

DOWNLOADER_MIDDLEWARES = {
	#'spyder.middleware.ProxyMiddleware': 100,
	#'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 112,
	'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware':541,
    'spyder.middleware.RequestsLimiter': 543,
}

ITEM_PIPELINES = {
	'spyder.pipelines.DuplicatesFilter': 1,
	'spyder.pipelines.TextExtractor': 2,
	'spyder.pipelines.KeywordExtractor': 3,
	#'spyder.pipelines.Markov': 4,
	#'spyder.pipelines.PageClassifier': 5,
	'spyder.pipelines.DataWriter': 6
}

#DEPTH_PRIORITY = 1
#SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
#SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
ROBOTSTXT_OBEY = True
