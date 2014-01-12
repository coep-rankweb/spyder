# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class WebItem(Item):
	title = Field()
	url = Field()
	extracted_text = Field()
	meta_description = Field()
	link_set = Field()
	keywords = Field()
	raw_html = Field()
	proba = Field()	#probability distribution of classes
	predict = Field()	#predicted class
