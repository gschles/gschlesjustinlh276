
import sys
import os.path
import gzip
from glob import iglob

def scan_corpus(training_corpus_loc):
  """
  Scans through the training corpus and counts how many lines of text there are
  """
  for block_fname in iglob( os.path.join( training_corpus_loc, '*.gz' ) ):
    print >> sys.stderr, 'processing dir: ' + block_fname
    with gzip.open( block_fname ) as f:
      num_lines = 0
      for line in f:
        # remember to remove the trailing \n
        line = line.rstrip()
        num_lines += 1
      print >> sys.stderr, 'Number of lines in ' + block_fname + ' is ' + str(num_lines)

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
