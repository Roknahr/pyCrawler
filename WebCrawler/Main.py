from Helper import Helper
from WebCrawler import *

wc = WebCrawler()

#urls = wc.fetch_urls_from_source('http://wikipedia.org')

#url = wc.normalize_url('/', 'wiki.org')
#print(url)
print(1)
#wc.crawl()
#print(Helper.get_domain("http://stackoverflow.com/"))
#print(wc.get_disallowed_sites("http://stackoverflow.com/", "*"))
print(Helper.get_path('http://stackoverflow.com/test/ivc/test'))
if(wc.is_allowed("http://stackoverflow.com/test/ivc/test")):
    print('true')
else:
    print('false')
if(wc.is_allowed("http://stackoverflow.com/test/ivc/test")):
    print('true')
else:
    print('false')
print(2)