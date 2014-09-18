from urllib import request
import re




class Indexer():
    def parse_html(self, html):
        return self.get_text_from_http(html)

    def get_text_from_http(self, html):
        print (html[:20])
        re_text = re.compile("<p>(.+)</p>")
        return re_text.findall(html)


if __name__ == "__main__":
    ind = Indexer()
    url = "http://en.wikipedia.org/wiki/Murder_of_Joanna_Yeates"
    print("hej")
    print(ind.parse_html(request.urlopen(url)))
