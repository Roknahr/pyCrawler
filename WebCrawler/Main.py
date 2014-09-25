from WebCrawler import *

wc = WebCrawler()

#urls = wc.fetch_urls_from_source('http://wikipedia.org')

#url = wc.normalize_url('/', 'wiki.org')
#print(url)
wc.crawl()
#print(Helper.get_domain("http://us.rd.yahoo.com/finance/news/rss/story/*http://finance.yahoo.com/news/tokyo-gas-no-hurry-buy-113424587.html"))
#print(wc.get_disallowed_sites("http://stackoverflow.com/", "*"))
#if wc.is_allowed("ssl.reddit.com/res"):
#    print('true')
#else:
#    print('false')