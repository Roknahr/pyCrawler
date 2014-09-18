from urllib import request
from lib.dehtml import dehtml

class Indexer():
    def parse_html(self, html):
        return dehtml(html).replace('\\n', '').replace('\\t', '')

if __name__ == "__main__":
    ind = Indexer()
    url = "http://en.wikipedia.org/wiki/Murder_of_Joanna_Yeates"
    print("testing...")
    print(ind.parse_html(str(request.urlopen(url).read())))

