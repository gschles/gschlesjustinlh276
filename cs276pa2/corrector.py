
import sys, math
from collections import Counter
import cPickle

interp_weight = 0.2
edit_prob = 0.1
equal_prob = 0.9

queries_loc = 'data/queries.txt'
gold_loc = 'data/gold.txt'
google_loc = 'data/google.txt'

unigram_file = 'unigram'
bigram_file = 'bigram'

unigram_counts = Counter()
bigram_counts = Counter()
term_count = 0

alphabet = "abcdefghijklmnopqrstuvwxyz0123546789&$+_' "

def read_query_data():
  """
  all three files match with corresponding queries on each line
  """
  queries = []
  gold = []
  google = []
  with open(queries_loc) as f:
    for line in f:
      queries.append(line.rstrip())
  with open(gold_loc) as f:
    for line in f:
      gold.append(line.rstrip())
  with open(google_loc) as f:
    for line in f:
      google.append(line.rstrip())
  assert( len(queries) == len(gold) and len(gold) == len(google) )
  return (queries, gold, google)

def uni_cost_prob(r, q, dist):
  if q == r:
    return equal_prob
  else:
    return math.pow(uni_prob, dist)

def unigram_prob(word):
  return unigram_counts[word]/term_count

def bigram_prob(w1, w2):
  return bigram_counts[(w1, w2)]/unigram_counts[w1]

def interp_prob(w1, w2):
  if w1 is None:
    return unigram_prob(w2)
  else:
    return interp_weight*unigram_prob(w1) + (1 - interp_weight)*bigram_prob(w1, w2)

def query_prob(query):
  words = query.split()
  prob = 0
  w1 = None
  for w2 in words:
    prob += math.log(interp_prob(w1, w2))
    w1 = w2
  return prob

def read_models():
  """
  reads in unigram and bigram counts stored from buildmodels.sh
  """
  unigram = open(unigram_file, 'rb')
  bigram = open(bigram_file, 'rb')
  unigram_counts = cPickle.load(unigram)
  bigram_counts = cPickle.load(bigram)
  term_count = len(unigram_counts)

def main(argv):
  read_models() # retrieve the language models

if __name__ == '__main__':
  print(sys.argv)
  main(sys.argv)
