
import sys
import os.path
import gzip
import cPickle
from glob import iglob
from collections import Counter, defaultdict

def scan_corpus(training_corpus_loc):
  """
  Scans through the training corpus and counts how many lines of text there are
  Functionality added by Garrett: now counts all unigrams
  """
  unigram_counts = Counter()
  bigram_counts = Counter()

  for block_fname in iglob( os.path.join( training_corpus_loc, '*.gz' ) ):
    print >> sys.stderr, 'processing dir: ' + block_fname
    with gzip.open( block_fname ) as f:
      num_lines = 0
      for line in f:
        # remember to remove the trailing \n
        line = line.rstrip()
        words = line.split()
        prev_word = None
        for word in words:
          unigram_counts[word] += 1
          if prev_word is not None:
            bigram_counts[(prev_word, word)] += 1
          prev_word = word
        num_lines += 1
      print >> sys.stderr, 'Number of lines in ' + block_fname + ' is ' + str(num_lines)
  unigram_file = open('unigrams', 'wb')
  bigram_file = open('bigrams', 'wb')
  cPickle.dump(unigram_counts, unigram_file)
  cPickle.dump(bigram_counts, bigram_file)
  print >> sys.stderr, 'Processed ' + str(sum(unigram_counts.itervalues())) + ' tokens'
  print  >> sys.stderr, 'Processed ' + str(len(unigram_counts)) + ' unique types'
  print >> sys.stderr, 'Processed ' + str(sum(bigram_counts.itervalues())) + ' bigrams'
  print  >> sys.stderr, 'Processed ' + str(len(bigram_counts)) + ' unique bigrams'

class EmpiricalModel:
  def __init__(self):
    self.del_dic = defaultdict(lambda : 1)
    self.ins_dic = defaultdict(lambda : 1)
    self.sub_dic = defaultdict(lambda : 1)
    self.trans_dic = defaultdict(lambda : 1)
    self.count_dic = defaultdict(lambda : 0)
    self.edit1s = []

  def read_edit1s(self, edit1s_loc):
    """
    Returns the edit1s data
    It's a list of tuples, structured as [ .. , (misspelled query, correct query), .. ]
    """
    with gzip.open(edit1s_loc) as f:
      # the .rstrip() is needed to remove the \n that is stupidly included in the line
      self.edit1s = [ line.rstrip().split('\t') for line in f if line.rstrip() ]
    return
    
  def build_empirical_model(self):
    for edit in self.edit1s:
      self.update_counts(edit[1])
      if edit[0] == edit[1]:
        continue
      (edit_type, edit_arg) = self.compute_edit_type(edit[0], edit[1])
      if edit_type == 'del':
        self.del_dic[edit_arg] +=1
      elif edit_type == 'ins':
        self.ins_dic[edit_arg] +=1
      elif edit_type == 'sub':
        self.sub_dic[edit_arg] +=1
      elif edit_type == 'trans':
        self.trans_dic[edit_arg] +=1

  def compute_edit_type(self, incor, cor):
    edit_type = None
    edit_arg = None
    if len(incor) < len(cor):
      edit_type = 'del'
      edit_arg = self.find_del_arg(incor, cor)
    elif len(incor) > len(cor):
      edit_type = 'ins'
      edit_arg = self.find_ins_arg(incor, cor)
    else:
      (edit_type, edit_arg) = self.compute_sub_trans(incor, cor)
    return edit_type, edit_arg

  def compute_sub_trans(self, incor, cor):
    edit_type = None
    edit_arg = None
    ind = self.find_discrep(incor, cor)
    if ind == len(incor) - 1:
      edit_type = 'sub'
      edit_arg = incor[ind]+cor[ind]
    elif incor[ind+1] == cor[ind+1]:
      edit_type = 'sub'
      edit_arg = incor[ind]+cor[ind]
    else:
      edit_type = 'trans'
      edit_arg = cor[ind:ind+2]
    return edit_type, edit_arg

  def find_discrep(self, incor, cor):
    for i in range(0,min(len(incor), len(cor))):
      if incor[i] != cor[i]:
        return i
    return max(len(incor), len(cor)) - 1

  def find_del_arg(self, incor, cor):
    ind = self.find_discrep(incor, cor) - 1
    if ind == -1:
      return '$' + cor[0]
    else:
      return cor[ind:ind+2]
   
  def find_ins_arg(self, incor, cor):
    ind = self.find_discrep(incor, cor) - 1
    if ind == -1:
      return '$' + incor[0]
    else:
      return incor[ind:ind+2]

  def update_counts(self, query):
    prev = '$'
    for i in range(0,len(query)):
      cur = query[i]
      self.count_dic[cur] += 1
      if prev is not None:
        self.count_dic[prev+cur] += 1
      prev = cur
    self.count_dic[query[len(query)-1]+'$'] += 1
    
  def write_model_to_files(self):
    del_file = open('del', 'wb')
    cPickle.dump(dict(self.del_dic), del_file)
    ins_file = open('ins', 'wb')
    cPickle.dump(dict(self.ins_dic), ins_file)
    sub_file = open('sub', 'wb')
    cPickle.dump(dict(self.sub_dic), sub_file)
    trans_file = open('trans', 'wb')
    cPickle.dump(dict(self.trans_dic), trans_file)
    count_file = open('count', 'wb')
    cPickle.dump(dict(self.count_dic), count_file)

def main(argv):
  scan_corpus(argv[1]) #uncomment after empirical edits are done
  emp_model = EmpiricalModel()
  emp_model.read_edit1s(argv[2])
  emp_model.build_empirical_model()
  print >> sys.stderr, 'constructed empirical cost model... writing to file'
  emp_model.write_model_to_files()

if __name__ == '__main__':
  main(sys.argv)
