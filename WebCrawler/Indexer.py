from lib.dehtml import dehtml
from Term import Term
import sqlite3


from Stemmer import Stemmer
stop_words = set("""a about above after again against all am an and any are aren't as at
                be because been before being below between both but by can't cannot could
                couldn't did didn't do does doesn't doing don't down during each few for
                from further had hadn't has hasn't have haven't having he he'd he'll he's
                her here here's hers herself him himself his how how's i i'd i'll i'm
                i've if in into is isn't it it's its itself let's me more most mustn't
                my myself no nor not of off on once only or other ought our yourselves
                ours ourselves out over own same shan't she she'd she'll she's should
                shouldn't so some such than that that's the their theirs them themselves
                then there there's these they they'd they'll they're they've this those
                through to too under until up very was wasn't we we'd we'll we're we've
                were weren't what what's when when's where where's which while who who's
                whom why why's with won't would wouldn't you you'd you'll you're you've
                your yours yourself

                af alle andet andre at begge da de den denne der deres det dette dig din
                dog du ej eller en end ene eneste enhver et fem fire flere fleste for
                fordi forrige fra få før god han hans har hendes her hun hvad hvem hver
                hvilken hvis hvor hvordan hvorfor hvornår i ikke ind ingen intet jeg jeres
                kan kom kommer lav lidt lille man mand mange med meget men mens mere mig
                ned ni nogen noget ny nyt nær næste næsten og op otte over på se seks ses
                som stor store syv ti til to tre ud var er

                . [ ] ... ^ , " / ( ) == || // += && !=""".split())


class Indexer():
    dictionary = dict()

    def index(self):
        db = sqlite3.connect("data/pages.db")
        cursor = db.cursor()
        cursor.execute("""DROP TABLE IF EXISTS freqTable""")
        cursor.execute("""
            CREATE TABLE freqTable (id INTEGER PRIMARY KEY, term TEXT, freq INTEGER)
            """)
        cursor.execute("""DROP TABLE IF EXISTS indexTable""")
        cursor.execute("""
            CREATE TABLE indexTable (id INTEGER PRIMARY KEY, pageId INTEGER, termId INTEGER)
            """)

        cursor.execute("""SELECT id, html FROM pages""")
        id_html = cursor.fetchall()
        for i, html in id_html:
            if int(i) % 10 == 0:
                print(i)

            self.add_to_index(self.parse_html(str(html)), i)

        for key in self.dictionary.keys():
            cursor.execute("""
                INSERT INTO freqTable(term, freq) VALUES (?,?)
                """, (key, self.dictionary[key].freq))
            term_id = cursor.lastrowid
            if int(term_id) % 1000 == 0:
                print(term_id)
            for page_id in self.dictionary[key].getPostList():
                cursor.execute("""
                    INSERT INTO indexTable(pageId, termId) VALUES (?,?)""", (page_id, term_id))

        db.commit()
        db.close()

    @staticmethod
    def parse_html(html):
        words = dehtml(html)

        s = Stemmer("danish")

        result = []
        for w in words.split():
            word = w.lower()
            if word in stop_words or len(word) < 2 or word.count('\\'):
                continue

            result.append(s.stemWord(word))
        return result

    def add_to_index(self, words, doc_id):
        for sw in words:
            if sw in self.dictionary.keys():
                self.dictionary[sw].freq += 1
            else:
                self.dictionary[sw] = Term()
                self.dictionary[sw].freq = 1
                self.dictionary[sw].name = sw
            self.dictionary[sw].addToPostList(doc_id)


if __name__ == "__main__":
    ind = Indexer()
    ind.index()
    url = "http://aau.dk/"
    print("testing...")

    res = sorted(ind.dictionary.values(), key=lambda x: x.freq)

    for r in res[-20:]:
        print(r.freq, r.name)

    print('total terms: ' + str(len(res)))