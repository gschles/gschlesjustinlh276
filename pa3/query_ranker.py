import sys, math, collections
import corpus_info
from query_parser import QueryParser, Query, Document

"""Parameters"""

# cosine similarity
C1 = 2.29
C2 = 0.1
C3 = 4.5

# BM25
Bt = 0.6
Bb = 0.5
Ba = 0.3
Wt = 2.2
Wb = 0.3
Wa = 4.0
K1 = 1.6

Lb = 0
Lt = 0
La = 0

norm_types = ('l1', 'sub', 'l1') # normalize title and anchor by L1, body by sublinear

TrainingQueries = {}
DocFreqs = {}
NumDocs = 0
Queries = {}

class TestQueryParser:

  def __init__(self, filename):
    self.queries = collections.defaultdict(lambda : None)
    self.tmp_query = ''
    self.load_queries(filename)

  def get_queries(self):
    return self.queries

  def load_queries(self, filename):
    f = open(filename, 'r')
    for line in f:
      line = line.strip()
      (type, body) = self.parse_line(line)
      if type == 'query':
        self.queries[body] = TestQuery(body)
        self.tmp_query = body
      elif type == 'url':
        self.queries[self.tmp_query].add_url(body)

  def parse_line(self, line):
    ind = line.find(':')
    return line[:ind], line[ind+1:].strip()

def idf(term):
  return math.log10(float(NumDocs+1.0)/DocFreqs[term])

class TestQuery:

  def __init__(self, text):
    self.query = text
    self.urls = []
    self.idf = [idf(term) for term in self.query.split()]

  def get_query(self):
    return self.query

  def add_url(self, url):
    self.urls.append(url)

  def get_idf(self):
    return self.idf

  def get_urls(self):
    return self.urls

def normalize_traindocs():
  for q in TrainingQueries:
    TrainingQueries[q].normalize_docs(norm_types)

def compute_average_field():
  num_titles = 0
  num_anchors = 0
  title_tot = 0
  anchor_tot = 0
  for k1, q in TrainingQueries.iteritems():
    docs = q.get_docs()
    for k2, d in docs.iteritems():
      if d.get_title():
        num_titles += 1
        title_tot += len(d.get_title())
      if d.get_anchor_length():
        num_anchors += 1
        anchor_tot += d.get_anchor_length()
  return float(title_tot)/num_titles, float(anchor_tot)/num_anchors

def load_globals(train_file, query_file):
  global TrainingQueries, DocFreqs, NumDocs, Lb, Queries, La, Lt
  parser = QueryParser(train_file)
  TrainingQueries = parser.get_queries()
  normalize_traindocs()
  corp_info = corpus_info.CorpusInfo()
  DocFreqs = corp_info.get_doc_freqs()
  NumDocs = corp_info.get_num_docs()
  Lb = corp_info.get_average_doc_length()
  (Lt, La) = compute_average_field()
  parser = TestQueryParser(query_file)
  Queries = parser.get_queries()

def rank(query, task):
  docs = TrainingQueries[query.get_query()].get_docs()
  print 'query: ' + query.get_query()
  rankings = []
  if task == 1:
    rankings = rank_cosine(query, docs)
  elif task == 2:
    rankings = rank_bm25(query, docs)
  elif task == 3:
    print >> sys.stderr, 'to do: implement smallest window'
  rankings.reverse()
  for r in rankings:
    print '\turl: ' + r[1]

def fdf(doc, type, term_ind):
  if type == 'title':
    if len(doc.get_title()) == 0:
      return 0
    return float(doc.get_title_tfs()[term_ind])/(1 + Bt*(float(len(doc.get_title()))/Lt - 1))
  elif type == 'body':
    if doc.get_body_length() == 0:
      return 0
    return float(doc.get_body_tfs()[term_ind])/(1 + Bb*(float(doc.get_body_length())/Lb - 1))
  elif type == 'anchor':
    if doc.get_anchor_length() == 0:
      return 0
    return float(doc.get_anchor_tfs()[term_ind])/(1 + Ba*(float(doc.get_anchor_length())/La - 1))

def bm25(term_ind, doc):
  wtd = sum([Wt*fdf(doc, 'title', term_ind), Wb*fdf(doc, 'body', term_ind), Wa*fdf(doc, 'anchor', term_ind)])
  return wtd*idf(doc.get_query()[term_ind])/(K1 + wtd)
  

def rank_bm25(query, docs):
  return sorted([(sum([bm25(i, docs[d]) for i in range(len(query.get_query().split()))]), d) for d in docs])

def cosine_similarity(u, v1, v2, v3):
  return sum([u[i]*(C1*v1[i] + C2*v2[i] + C3*v3[i]) for i in range(len(u))])

def rank_cosine(query, docs):
  #return sorted([(cosine_similarity(query.get_idf(), docs[d].get_title_tfs('norm'), docs[d].get_body_tfs('norm'), docs[d].get_anchor_tfs('norm')), d) for d in query.get_urls()])
  return sorted([(cosine_similarity(query.get_idf(), docs[d].get_title_tfs('norm'), docs[d].get_body_tfs('norm'), docs[d].get_anchor_tfs('norm')), d) for d in docs])

def main(argv):
  load_globals(argv[2], argv[4])
  for query in Queries:
    rank(Queries[query], int(argv[1]))

if __name__ == '__main__':
  main(sys.argv)