import math
import sqlite3
from Indexer import Indexer as ind


def rank_terms():
    db = sqlite3.connect("data/pages.db")
    cursor = db.cursor()

    cursor.execute("""SELECT COUNT(*) FROM freqTable""")
    n = cursor.fetchall()[0][0]

    cursor.execute("""SELECT term, freq FROM freqTable""")
    #df_t = {}
    inverse_doc_freq = {}
    for r in cursor.fetchall():
        #df_t[r[0]] = r[1]
        inverse_doc_freq[r[0]] = math.log10(n / r[1])

    db.close()
    return inverse_doc_freq

times = [[], [], []]
def do_query(query, idf_t):
    q_terms = set(ind.parse_html(query))

    db = sqlite3.connect("data/pages.db")
    cursor = db.cursor()

    page_ids = set()

    for term in q_terms:
        db_q = """SELECT indexTable.pageId FROM indexTable, freqTable
            WHERE freqTable.id = indexTable.termID
            AND freqTable.term = "{0}"
            """.format(term)
        cursor.execute(db_q)

        tmp_page_ids = set()
        if len(page_ids) == 0:
            for page_id in cursor.fetchall():
                page_ids.add(page_id[0])
        else:
            for page_id in cursor.fetchall():
                tmp_page_ids.add(page_id[0])
            page_ids = page_ids.intersection(tmp_page_ids)

    import time
    page_score = []
    i = 0.0

    for page_id in page_ids:
        t = time.time()
        db_q = """SELECT html FROM htmlParsed WHERE pageId = ?"""
        cursor.execute(db_q, (page_id,))
        times[0].append(time.time() - t)
        doc = str(cursor.fetchall()[0][0]).split()  # ind.parse_html(str(cursor.fetchall()[0][0]))
        times[1].append(time.time() - t)
        page_score.append((page_id, compare_page_query(doc, ind.parse_html(query), idf_t)))
        times[2].append(time.time() - t)
        print('{1:.2%} {0}'.format(page_id, 1.0/len(page_ids)*i), end='\r')
        i += 1

    db.close()
    return page_score


def compare_page_query(doc, query, idf_t):
    d_terms = set(doc)
    q_terms = set(query)

    terms = q_terms.union(d_terms)

    q_tf_wt = {}
    q_wt = {}
    d_tf_wt = {}
    d_wt = {}
    for t in terms:
        q_tf_wt[t] = 1 + math.log10(query.count(t)) if query.count(t) > 0 else 0  # l for q
        q_wt[t] = q_tf_wt[t] * idf_t[t]  # t for q

        d_tf_wt[t] = 1 + math.log10(doc.count(t)) if doc.count(t) > 0 else 0  # l for d
        d_wt[t] = d_tf_wt[t]  # n for d

    f = lambda x: x * x
    q_length = math.sqrt(sum(map(f, q_wt.values())))  # c for q
    d_length = math.sqrt(sum(map(f, d_wt.values())))  # c for d

    q_norm_wt = {}
    d_norm_wt = {}
    res = 0
    for t in terms:
        q_norm_wt[t] = q_wt[t] / q_length  # c for q
        d_norm_wt[t] = d_wt[t] / d_length  # c for d

        res += q_norm_wt[t] * d_norm_wt[t]
    return res


if __name__ == '__main__':
    q = "trigger code"

    _idf_t = rank_terms()
    scores = do_query(q, _idf_t)
    scores.sort(key=lambda x: x[1])

    db = sqlite3.connect("data/pages.db")
    cursor = db.cursor()
    if len(scores) < 10:
        for page in scores:
            cursor.execute("""SELECT url FROM pages WHERE id = ?""", (page[0],))
            url = cursor.fetchall()[0][0]
            print(url + '  ' + str(page[1]))
    else:
        for page in scores[-10:]:
            cursor.execute("""SELECT url FROM pages WHERE id = ?""", (page[0],))
            url = cursor.fetchall()[0][0]
            print(url + '  ' + str(page[1]))
    db.close()

    print(str(len(times[0])) + " Pages compared")
    for ti in times:
            print("avg: " + str(sum(ti)/len(ti)) + "  max: " + str(max(ti)) + "  sum: " + str(sum(ti)))
