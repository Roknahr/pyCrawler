import re
import os
import sqlite3
from urllib import request
from fnmatch import fnmatch

from Helper import Helper
from Frontier import Frontier

class WebCrawler:

    frontier = Frontier()
    all_urls = []

    robots = {}

    def __init__(self):
        if not os.path.exists("data"):
            os.makedirs("data")

        db = sqlite3.connect("data/pages.db")
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages(id INTEGER PRIMARY KEY, url TEXT, html TEXT)
        """)
        cursor.execute("""SELECT url FROM pages""")
        self.all_urls = [''.join(item) for item in cursor.fetchall()]
        db.commit()
        db.close()

        #self.frontier.put(self.normalize_url("/questions/2023893/python-3-get-http-page", "stackoverflow.com"))

        for url in self.all_urls:
            self.frontier.put(url)
        self.frontier.fill_back_queue()


    def crawl(self):
        dblength = 0

        while dblength <= 100:
            url = self.frontier.get()
            print(url)
            tempUrls = self.process_url(url)

            #For simplicity: We do not want to crawl pages we already crawled in this session.
            tempList = list(tempUrls - set(self.all_urls))

            for url in tempList:
                self.frontier.put(url)

            db = sqlite3.connect("data/pages.db")
            cursor = db.cursor()
            cursor.execute("""SELECT url FROM pages""")
            dblength = len(cursor.fetchall())
            print(dblength)
            db.close()

    def is_allowed(self, url):
        disallowed = self.get_disallowed_sites(url, 'GingerWhiskeyCrawler')
        urlpath = Helper.get_path(url)
        for path in disallowed:
            if fnmatch(urlpath, path):
                result = False
                break
            else:
                result = True
        return result

    def get_disallowed_sites(self, url, myAgent):
        domain = Helper.get_domain(url)

        if domain in self.robots.keys():
            return self.robots[domain]

        try:
            robot = request.urlopen('http://' + domain + '/robots.txt')
            print(1.5)
        except:
            return []

        reAgent = re.compile("User-[aA]gent: *(\S+) *$")
        reDis = re.compile("Disallow: *(/\S*) *$")

        agent = None
        disallowed = {}

        for line in robot:
            l = str(line).replace("\\n", "").replace("\\r", "")[:-1]
            if reAgent.findall(l): 
                agent = reAgent.findall(l)[0]
                disallowed[agent] = []
            if reDis.findall(l): 
                disallowed[agent].append(reDis.findall(l)[0])
            
        result = []
        if myAgent in disallowed:
            for link in disallowed[myAgent]:
                result.append(link)  # self.normalize_url(link, domain))
        if '*' in disallowed:
            for link in disallowed['*']:
                result.append(link)  # self.normalize_url(link, domain))

        self.robots[domain] = result
        return result

    def normalize_url(self, url, root_domain):
        new_url = self.expand_url(url, root_domain)
        new_url = self.set_case(new_url)
        return new_url
 
 
    def expand_url(self, url, root_domain):
        root_domain = 'http://' + root_domain
        url_new = url

        if len(url) > 1 and url[0] == '/':
            if url[1] == '/':
                url_new = 'http:' + url
            else:
                url_new = root_domain + url
        elif len(url) <= 1:
            url_new = root_domain + '/'

        return url_new    

    def process_url(self, url):
        try:
            source = request.urlopen(url).read()
        except:
            return set()
        db = sqlite3.connect("data/pages.db")
        cursor = db.cursor()
        cursor.execute("""SELECT url FROM pages""")
        all_urls = [''.join(item) for item in cursor.fetchall()]
        if url in all_urls:
            cursor.execute("""
                UPDATE pages SET html = ? WHERE url = ? """, (source, url))
        else:
            cursor.execute("""
                INSERT INTO pages(url, html) VALUES (?,?)""", (url, source))
        db.commit()
        db.close()

        # Regex for finding links
        rgx = re.compile('a href="(\/\S+|[\/aA-zZ0-9]\S+\.\S+)"')

        linkMatches = rgx.findall(str(source))

        tempFrontier = set()

        tempFrontier.add(url)

        if self.frontier.frontQueue.qsize() < 100:
            for link in linkMatches:
                tempFrontier.add(self.normalize_url(link, Helper.get_domain(url)))
        
        #tempFrontier = tempFrontier - set(self.get_disallowed_sites(url, 'GingerWhiskeyCrawler'))

        return tempFrontier

 
    def set_case(self, url):
        """ Fix case of protocol and domain."""
        i = 0
        tempCharList = []
            
        # set protocol and host to lower case
        while(i < len(url)):
            #print(str(len(url)))
            tempCharList.append(url[i].lower())

            if i > 0 and url[i] == '/' and not (url[i - 1] == ':' or url[i - 1] == '/'):
                i += 1
                break
            
            i += 1
        
        # the -2 is to avoid an index out of bound exception. The code continues from after the domain
        while(i < len(url)):
            tempCharList.append(url[i])

            if url[i] == '%' and i < len(url)-2:
                tempCharList.append(url[i+1].upper())
                tempCharList.append(url[i+2].upper())
                i += 2

            i += 1

        tempUrl = ''.join(tempCharList)

        # replace octets
        tempUrl.replace("%7E", "~")
        tempUrl.replace("%2D", "-")
        tempUrl.replace("%2E", ".")
        tempUrl.replace("%5F", "_")

        return tempUrl
        