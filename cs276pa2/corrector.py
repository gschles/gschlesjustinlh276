import sys, math
from collections import Counter, defaultdict
import cPickle
from time import clock

uniform_prob = "uniform"
empirical_prob = "empirical"
stupid = False
laplace = False

interp_weight = 0.1
edit_prob = 0.01
equal_prob = 0.95
stupid_discount = 0.01

queries_loc = 'data/queries.txt'
#queries_loc = 'wrong'
gold_loc = 'data/gold.txt'
google_loc = 'data/google.txt'

unigram_file = 'unigrams'
bigram_file = 'bigrams'
del_file = 'del'
ins_file = 'ins'
sub_file = 'sub'
trans_file = 'trans'
count_file = 'count'

unigram_counts = Counter()
bigram_counts = Counter()
del_dic = defaultdict(lambda:1)
ins_dic = defaultdict(lambda:1)
sub_dic = defaultdict(lambda:1)
trans_dic =defaultdict(lambda:1)
count_dic = defaultdict(lambda:0)
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
    return math.pow(edit_prob, dist)

def unigram_prob(string):
  return float(unigram_counts[string])/term_count

def bigram_prob(w1, w2):
  return float(bigram_counts[(w1, w2)])/unigram_counts[w1]

def interp_prob(w1, w2):
  if w1 is None:
    return unigram_prob(w2)
  else:
    return interp_weight*unigram_prob(w1) + (1 - interp_weight)*bigram_prob(w1, w2)

def stupid_prob(w1, w2):
  if w1 is None:
    return unigram_prob(w2)
  else:
    prob = bigram_prob(w1, w2)
    if prob > 0:
      return prob
    else:
      return stupid_discount*unigram_prob(w2)

def laplace_prob(w1, w2):
  if w1 is None:
    return unigram_prob(w2)
  else:
    return float(bigram_counts[(w1,w2)]+1)/(unigram_counts[w1]+term_count)

def query_prob(query):
  strings = query.split()
  prob = 0
  w1 = None
  for w2 in strings:
    if stupid:
      prob += math.log(stupid_prob(w1,w2))
    elif laplace:
      prob += math.log(laplace_prob(w1,w2))
    else:
      prob += math.log(interp_prob(w1, w2))
    w1 = w2
  return prob

def read_models():
  """
  reads in unigram and bigram counts stored from buildmodels.sh
  reads in empircal edit cost dictionaries stored from buildmodels.sh
  """
  global unigram_counts, bigram_counts, term_count, del_dic, ins_dic, sub_dic, tras_dic, count_dic

  unigram = open(unigram_file, 'rb')
  bigram = open(bigram_file, 'rb')
  delete = open(del_file, 'rb')
  insert = open(ins_file, 'rb')
  subs = open(sub_file, 'rb')
  trans = open(trans_file, 'rb')
  count = open(count_file, 'rb')
  unigram_counts = cPickle.load(unigram)
  bigram_counts = cPickle.load(bigram)
  term_count = len(unigram_counts)
  del_dic.update(cPickle.load(delete))
  ins_dic.update(cPickle.load(insert))
  sub_dic.update(cPickle.load(subs))
  trans_dic.update(cPickle.load(trans))
  count_dic.update(cPickle.load(count))


alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789 +\'-_$&'

#returns list of tuples of form ("query","edit_type","edit_arg")
def empirical_edits1(string):
   splits     = [(string[:i], string[i:]) for i in range(len(string) + 1)]
   deletes    = [(a + b[1:],'del',a[-1] + b[0]) for a, b in splits if a and b]
   deletes1   = [(b[1:],'del','$' + b[0]) for a, b in splits if not a and b]
   transposes = [(a + b[1] + b[0] + b[2:],'trans',b[0] + b[1]) for a, b in splits if len(b)>1]
   replaces   = [(a + c + b[1:],'sub',b[0] + c) for a, b in splits for c in alphabet if b]
   inserts    = [(a + c + b,'ins',a[-1] + c)    for a, b in splits for c in alphabet if a]
   inserts1   = [(c + b,'ins','$' + c)    for a, b in splits for c in alphabet if not a]
   return deletes + deletes1 + transposes + replaces + inserts + inserts1

def edits1(string):
   splits     = [(string[:i], string[i:]) for i in range(len(string) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)
   
def edits2(string):
    return set(e2 for e1 in edits1(string) for e2 in edits1(e1) )

def is_valid_query(query):
    if query.find('  ') >= 0:
        return False

    words = query.split()
    for word in words:
        if word not in unigram_counts:
            return False
    return True

def uniform_query_prob(query,candidate_query,edits):
    q_prob = query_prob(candidate_query)
    if query == candidate_query:
        return q_prob + math.log(equal_prob)
    else:
        return q_prob + math.log(math.pow(edit_prob, edits))

def find_uniform_correction(query):
    candidate_edit1_queries = edits1(query)
    candidate_edit1_queries = set(q for q in candidate_edit1_queries if is_valid_query(q)) 
    max_query = ''
    max_query_prob = None
    if is_valid_query(query):
      max_query = query
      max_query_prob = uniform_query_prob(query, query, 0)
    for curr_query in candidate_edit1_queries:
        curr_query_prob = uniform_query_prob(query, curr_query,1)
        if curr_query_prob > max_query_prob:
            max_query = curr_query
            max_query_prob = curr_query_prob
    if max_query != '':
	return max_query
    candidate_edit2_queries = edits2(query)
    candidate_edit2_queries = set(q for q in candidate_edit2_queries if is_valid_query(q))
    for curr_query in candidate_edit2_queries:
        curr_query_prob = uniform_query_prob(query, curr_query,2)
        if curr_query_prob > max_query_prob:
            max_query = curr_query
            max_query_prob = curr_query_prob
    return max_query


def empirical_edit_prob(candidate_query_tuple):
    edit_type = candidate_query_tuple[1]
    edit_arg = candidate_query_tuple[2]
    if edit_type == 'ins':
        return math.log((float(ins_dic[edit_arg])/(count_dic[edit_arg[0]]+len(alphabet))))
    elif edit_type == 'sub':
        return  math.log((float(sub_dic[edit_arg])/(count_dic[edit_arg[0]]+len(alphabet))))
    elif edit_type == 'del':
        return math.log((float(del_dic[edit_arg])/(count_dic[edit_arg]+len(alphabet)*(len(alphabet)-1))))
    elif edit_type == 'trans':
        return math.log((float(trans_dic[edit_arg])/(count_dic[edit_arg]+len(alphabet)*(len(alphabet)-1))))

def empirical_query_prob(candidate_query_tuple):
    return  query_prob(candidate_query_tuple[0]) + empirical_edit_prob(candidate_query_tuple)
    
def find_empirical_edit1_correction(candidate_query_tuples):
    max_query = ""
    max_query_prob = None
    for curr_query_tuple in candidate_query_tuples:
        curr_query_prob = empirical_query_prob(curr_query_tuple)
        if curr_query_prob > max_query_prob:
            max_query = curr_query_tuple[0]
            max_query_prob = curr_query_prob
    return (max_query, max_query_prob)

# calculates the
def find_empirical_correction(original_query):
    max_query_prob = None
    max_query = ''
    
    #default max_query to uniform model
    if is_valid_query(original_query):
      max_query_prob = uniform_query_prob(original_query, original_query, 0)
      max_query = original_query
    
    #check all queries one edit distance away for improvement on max_query_prob
    candidate_edit1_query_tuples = empirical_edits1(original_query)
    candidate_edit1_query_tuples_cleaned = [q for q in candidate_edit1_query_tuples if is_valid_query(q[0])]
    (max_query1, max_query_prob1) = find_empirical_edit1_correction(candidate_edit1_query_tuples_cleaned)
    if max_query_prob1 > max_query_prob:
      max_query_prob = max_query_prob1
      max_query = max_query1

    if max_query != '':
      return max_query
    
    #check all queries two edit distance away for improvement on max_query_prob
    for curr_edit1_query_tuple in candidate_edit1_query_tuples:
        candidate_edit2_query_tuples = empirical_edits1(curr_edit1_query_tuple[0])
        candidate_edit2_query_tuples_cleaned = [q for q in candidate_edit2_query_tuples if is_valid_query(q[0])]
        if candidate_edit2_query_tuples_cleaned != []:
		(max_edit2_query, max_edit2_query_prob) = find_empirical_edit1_correction(candidate_edit2_query_tuples_cleaned)
        	total_max_edit2_query_prob = max_edit2_query_prob + empirical_edit_prob(curr_edit1_query_tuple) 
        	if total_max_edit2_query_prob > max_query_prob:
            		max_query = max_edit2_query
            		max_query_prob = max_edit2_query_prob
    return max_query
   
def main(argv):
  global stupid, laplace
  start = clock()
  prob_type = argv[2]
  if len(argv) >= 5:
    if argv[4] == 'stupid':
      stupid = True
    elif argv[4] == 'laplace':
      laplace = True
  read_models() # retrieve the language models
  (queries, gold, google) = read_query_data()
  
  for query in queries:
    query = query.strip()
    result = ''
    if prob_type == uniform_prob:
        result = find_uniform_correction(query)
    elif prob_type == empirical_prob:
        result = find_empirical_correction(query)
    if result == '':
        result = query
    print >> sys.stdout, result
  end = clock()
  print >> sys.stderr, str(end-start)
  
if __name__ == '__main__': main(sys.argv)



