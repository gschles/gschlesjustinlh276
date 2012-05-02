
import sys
import os.path
import gzip
from glob import iglob
from collections import Counter

def scan_corpus(training_corpus_loc):
  """
  Scans through the training corpus and counts how many lines of text there are
  Functionality added by Garrett: now counts all unigrams
  """
  word_counts = Counter()
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
          word_counts[word] += 1
          if prev_word is not None:
            bigram_counts[(prev_word, word)] += 1
          prev_word = word
        num_lines += 1
      print >> sys.stderr, 'Number of lines in ' + block_fname + ' is ' + str(num_lines)
  print >> sys.stderr, 'Processed ' + str(sum(word_counts.itervalues())) + ' tokens'
  print  >> sys.stderr, 'Processed ' + str(len(word_counts)) + ' unique types'
  print >> sys.stderr, 'Processed ' + str(sum(bigram_counts.itervalues())) + ' bigrams'
  print  >> sys.stderr, 'Processed ' + str(len(bigram_counts)) + ' unique bigrams'

def read_edit1s():
  """
  Returns the edit1s data
  It's a list of tuples, structured as [ .. , (misspelled query, correct query), .. ]
  """
  edit1s = []
  with gzip.open(edit1s_loc) as f:
    # the .rstrip() is needed to remove the \n that is stupidly included in the line
    edit1s = [ line.rstrip().split('\t') for line in f if line.rstrip() ]
  return edit1s

if __name__ == '__main__':
  print(sys.argv)
  scan_corpus(sys.argv[1])
