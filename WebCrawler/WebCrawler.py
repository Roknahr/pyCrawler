import re
import os
import sqlite3
from urllib import request
from fnmatch import fnmatch

from Helper import Helper
from Frontier import Frontier

class WebCrawler:
    # Set debug on or off - print debug msg with Helper.debug(str) if on.
    Helper.set_debug('off')

    
    frontier = Frontier()
    all_urls = []
    been_crawled = []

    tempDBCache = {}
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

        # Clean db
        cursor.execute("""DELETE FROM pages WHERE html = ''""")
        db.commit()
        db.close()

        # Seed
        if len(self.all_urls) == 0:
            self.frontier.put(self.normalize_url("/", "reddit.com"))
            self.frontier.put(self.normalize_url("/", "eb.dk"))

        for url in self.all_urls:
            if self.is_allowed(url):
                self.frontier.put(url)
        
        self.frontier.fill_back_queue()

    def clean_db(self):
        db = sqlite3.connect("data/pages.db")
        cursor = db.cursor()
        cursor.execute("""DELETE FROM pages WHERE html = ''""")
        cursor.execute("""SELECT url FROM pages""")
        entries = len(cursor.fetchall())
        db.commit()
        db.close()  

        if entries < 1000:
            self.crawl()

    def syncdb(self):
        db = sqlite3.connect("data/pages.db")
        cursor = db.cursor()
        cursor.execute("""SELECT url FROM pages""")
        all_urls = [''.join(item) for item in cursor.fetchall()]
        dbsize = len(all_urls)

        for url in self.tempDBCache:
            if url in all_urls:
                cursor.execute("""
                    UPDATE pages SET html = ? WHERE url = ? """, (self.tempDBCache[url], url))
            else:
                cursor.execute("""
                    INSERT INTO pages(url, html) VALUES (?,?)""", (url, self.tempDBCache[url]))
                dbsize += 1
        db.commit()
        db.close()


        return dbsize


    def crawl(self):
        dbsize = 0
        dbupdate = 0

        while dbsize <= 1000:
            url = self.frontier.get()
            print(url)
            tempUrls = self.process_url(url)

            # For simplicity: We do not want to crawl pages we already crawled in this session.
            tempList = list(tempUrls - set(self.been_crawled))
            self.been_crawled.append(url)

            for url in tempList:
                if self.is_allowed(url):
                    self.frontier.put(url)
            
            if dbupdate == 0:
                dbsize = self.syncdb()
                print(dbsize)

            dbupdate = (dbupdate + 1) % 210

        self.clean_db()

    def is_allowed(self, url):
        """ Returns ``True`` if allowed (not in robots.txt) - else returns ``False``. """
        disallowed = self.get_disallowed_sites(url, 'GingerWhiskeyCrawler')
        urlpath = Helper.get_path(url)
        result = True
        for path in disallowed:
            if path[-1] == '/':
                path += '*'
            if fnmatch(urlpath, path):
                result = False
                break

        return result

    def get_disallowed_sites(self, url, myAgent):
        Helper.debug("Get disallowed sites 1")

        domain = Helper.get_domain(url)

        if domain in self.robots.keys():
            return self.robots[domain]

        try:
            robot = request.urlopen('http://' + domain + '/robots.txt')
            Helper.debug('    Fetching robots.txt: '+domain)
        except:
            return []

        reAgent = re.compile("User-[aA]gent: *(\S+) *$")
        reDis = re.compile("Disallow: *(/\S*) *$")

        agent = None
        disallowed = {}
        Helper.debug("Get disallowed sites 2")
        for line in robot:
            l = str(line).replace("\\n", "").replace("\\r", "")[:-1]
            if reAgent.findall(l): 
                agent = reAgent.findall(l)[0]
                disallowed[agent] = []
            if reDis.findall(l): 
                if agent in disallowed:
                    disallowed[agent].append(reDis.findall(l)[0])
        Helper.debug("Get disallowed sites 3")    
        result = []
        if myAgent in disallowed:
            for link in disallowed[myAgent]:
                result.append(link)  # self.normalize_url(link, domain))
        if '*' in disallowed:
            for link in disallowed['*']:
                result.append(link)  # self.normalize_url(link, domain))
        Helper.debug("Get disallowed sites 4")
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

    def db_cache(self, url, source):
        if source:
            self.tempDBCache[url] = source

    def process_url(self, url):
        Helper.debug("process start")
        try:
            source = request.urlopen(url).read()
        except:
            return set()
        Helper.debug("process 1:db")
        
        self.db_cache(url, source)

        #db = sqlite3.connect("data/pages.db")
        #cursor = db.cursor()
        #cursor.execute("""SELECT url FROM pages""")
        #all_urls = [''.join(item) for item in cursor.fetchall()]
        #if url in all_urls:
        #    cursor.execute("""
        #        UPDATE pages SET html = ? WHERE url = ? """, (source, url))
        #else:
        #    cursor.execute("""
        #        INSERT INTO pages(url, html) VALUES (?,?)""", (url, source))
        #db.commit()
        #db.close()
        
        Helper.debug("process 2:re")
        # Regex for finding links
        rgx = re.compile('a href="(\/\S+|[\/aA-zZ0-9]\S+\.\S+)"')

        linkMatches = rgx.findall(str(source))

        tempFrontier = set()

        tempFrontier.add(url)
        Helper.debug("process 3:add links")
        if self.frontier.frontQueue.qsize() < 10:
            for link in linkMatches:
                if ('https://' in link or 'http://' in link or link[0] == '/') \
                    and 'ftp.' not in link \
                    and'ftp://' not in link \
                    and 'mailto:' not in link:
                    tempFrontier.add(self.normalize_url(link, Helper.get_domain(url)))
        
        #tempFrontier = tempFrontier - set(self.get_disallowed_sites(url, 'GingerWhiskeyCrawler'))
        Helper.debug("process end")
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
        