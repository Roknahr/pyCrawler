from Helper import Helper
from WebCrawler import *

wc = WebCrawler()

#urls = wc.fetch_urls_from_source('http://wikipedia.org')

#url = wc.normalize_url('/', 'wiki.org')
#print(url)
#wc.crawl()
#print(Helper.get_domain("http://stackoverflow.com/"))
#print(wc.get_disallowed_sites("http://stackoverflow.com/", "*"))
if wc.is_allowed("reddit.com/u/Roknahr"):
    print('true')
else:
    print('false')