import math

class ContentRanker:
	vocabulary = "word1 word2 word3 word4 word5".split()
	
	docs = ["word4 word2 word2 word1 word4 word2 word3",
			"word1 word3 word4 word2 word5 word3 word1",
			"word2 word3 word4 word5 word1 word2",
			"word3 word4"]
	
	q = "word2"
	N = 0
	
	for doc in docs:
		for w in doc.split():
			N += 1
	
	print('N:' + str(N))
	
	df_t = {}
	for word in vocabulary:
		df_t[word] = 0
		for d in docs:
			df_t[word] += d.count(word)
	
	idf_t = {}
	for word in vocabulary:
		idf_t[word] = math.log10(N / df_t[word])
	
	
	# tf_idf = math.log10(1 + tf_td) * math.log10(N/df_t)
	
	def make_table(doc, query):
		dterms = set(doc.split())
		qterms = set(query.split())
	
		terms = qterms.union(dterms)
	
		q_tf_wt = {}
		q_wt = {}
		d_tf_wt = {}
		d_wt = {}
		for t in terms:
			q_tf_wt[t] = 1 + math.log10(query.count(t)) if query.count(t) > 0 else 0
			q_wt[t] = idf_t[t] * q_tf_wt[t]
	
			d_tf_wt[t] = 1 + math.log10(doc.count(t)) if doc.count(t) > 0 else 0
			d_wt[t] = d_tf_wt[t]  # Err?
	
		f = lambda x: x * x
		q_length = math.sqrt(sum(map(f, q_wt.values())))
		d_lenght = math.sqrt(sum(map(f, d_wt.values())))
	
		q_norm_wt = {}
		d_norm_wt = {}
		res = 0
		for t in terms:
			q_norm_wt[t] = q_wt[t] / q_length
			d_norm_wt[t] = d_wt[t] / d_lenght
	
			res += q_norm_wt[t] * d_norm_wt[t]
		return res
	
	i = 1
	for d in docs:
		print('doc' + str(i) + ': ' + str(make_table(d, q)))
		i += 1
		
	def __init__(self):
        pass
	
	


