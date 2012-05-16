import sys, math, collections

class QueryParser:

  def __init__(self, filename):
    f = open(filename, 'r')
    self.queries = collections.defaultdict(lambda : None)
    self.tmp_query = None
    self.build_queries(f)
  
  def get_queries(self):
    return self.queries

  def parse_line(self, line):
    ind = line.find(':')
    return line[0:ind].strip(), line[ind+1:].strip()

  def build_queries(self, f):
    for line in f:
      (type, body) = self.parse_line(line)
      if type == 'query':
        self.queries[body] = Query(body)
        self.tmp_query = body
      elif type == 'url':
        self.queries[self.tmp_query].add_doc(body)
      else:
        self.queries[self.tmp_query].modify_doc(type, body)

class Query:

  def __init__(self, text):
    self.query = text.split()
    self.docs = collections.defaultdict(lambda : None)
    self.tmp_url = None

  def add_doc(self, url):
    self.docs[url] = Document(url, self.query)
    self.tmp_url = url

  def get_query(self):
    return self.query

  def get_docs(self):
    return self.docs

  def modify_doc(self, type, body):
    self.docs[self.tmp_url].add_field(type, body)

  def normalize_docs(self, types):
    for d in self.docs:
      self.docs[d].normalize_all(types)

class Document:

  def __init__(self, text, query):
    self.query = query
    self.url = text
    self.title = None
    self.title_tfs = [0 for term in self.query]
    self.body_hits = collections.defaultdict(lambda : None)
    self.body_tfs = [0 for term in self.query]
    self.body_length = 0
    self.anchor_text = collections.defaultdict(lambda : 0)
    self.anchor_tfs = [0 for term in query]
    self.anchor_length = 0
    self.temp_text = None

  def get_query(self):
    return self.query

  def get_url(self):
    return self.url

  def get_title(self):
    return self.title

  def get_body_hits(self):
    return self.body_hits

  def get_body_length(self):
    return self.body_length

  def get_anchor_text(self):
    return self.anchor_text

  def get_anchor_length(self):
    return self.anchor_length

  def get_title_tfs(self,opt=None):
    if opt == 'norm':
      return self.title_tfs_norm
    return self.title_tfs

  def get_body_tfs(self,opt=None):
    if opt == 'norm':
      return self.body_tfs_norm
    return self.body_tfs

  def get_anchor_tfs(self,opt=None):
    if opt == 'norm':
      return self.anchor_tfs_norm
    return self.anchor_tfs

  def normalize_all(self, types):
    self.title_tfs_norm = self.normalize(self.title_tfs, types[0], len(self.title))
    self.body_tfs_norm = self.normalize(self.body_tfs, types[1], self.body_length)
    self.anchor_tfs_norm = self.normalize(self.anchor_tfs, types[2], self.anchor_length)

  def normalize(self, vec, type, l=1):
    if type == 'l1': # case: l1 norm
      return [float(vec[i])/l if l > 0 else 0 for i in range(len(vec))]
    elif type == 'sub': # case: sublinear tf scaling
      return [1.0 + math.log(val) if val > 0 else 0 for val in vec]

  def add_field(self, type, body):
    if type == 'title':
      self.title = body.split()
      for word in self.title:
        if word in self.query:
          self.title_tfs[self.query.index(word)] += 1
    elif type == 'body_hits':
      (term, hits) = self.parse_body_hits(body)
      self.body_hits[term] = hits
      for i, word in enumerate(self.query):
        if word == term: self.body_tfs[i] = len(hits)
    elif type == 'body_length':
      self.body_length = int(body)
    elif type == 'anchor_text':
      self.temp_text = tuple(body.split())
    elif type == 'stanford_anchor_count':
      self.anchor_text[self.temp_text] = int(body)
      self.anchor_length += len(self.temp_text)*int(body)
      for word in self.temp_text:
        if word in self.query:
          self.anchor_tfs[self.query.index(word)] += int(body)

  def parse_body_hits(self, text):
    hits = []
    l = text.split()
    term = l[0]
    for i in range(1,len(l)):
      hits.append(int(l[i]))
    return term, hits

"""
def main(argv):
  parser = QueryParser(argv[1])
  queries = parser.get_queries()
  for query in queries:
    docs = queries[query].get_docs()
    for doc in docs:
      print queries[query].query
      print docs[doc].get_title_tfs()
      print docs[doc].get_body_tfs()
      print docs[doc].get_anchor_tfs()

if __name__ == '__main__':
  main(sys.argv)
"""