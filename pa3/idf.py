import sys, os, collections

class Idf:

  def __init__(self, filename, corpus_loc):
    f = open(filename, 'r')
    self.terms = set([line.strip() for line in f])
    self.df = collections.defaultdict(lambda : 1)
    self.corpus_length = 0
    self.num_docs = 0
    self.scan_corpus(corpus_loc)
    self.average_doc_length = float(self.corpus_length)/self.num_docs
    print >> sys.stderr, 'processed ' + str(self.num_docs) + ' documents'
    print >> sys.stderr, 'average doc length: ' + str(self.average_doc_length)
    print self.average_doc_length
    for term in self.df:
      print term + '\t' + str(self.df[term])

  def scan_corpus(self, loc):
    for dir in sorted(os.listdir(loc)):
      print >> sys.stderr, 'processing dir: ' + dir
      dir_name = os.path.join(loc, dir)
      for filename in sorted(os.listdir(dir_name)):
        self.num_docs += 1
        fullpath = os.path.join(dir_name, filename)
        f = open(fullpath, 'r')
        doc_terms = set([])
        for line in f:
          tokens = line.strip().split()
          for token in tokens:
            self.corpus_length += 1
            if token in self.terms:
              if not token in doc_terms:
                self.df[token] += 1
                doc_terms.add(token)
        f.close()

def main(argv):
  idf = Idf(argv[1], argv[2])

if __name__ == '__main__':
  main(sys.argv)