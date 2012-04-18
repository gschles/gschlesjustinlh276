#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re
from array import array

if len(sys.argv) != 3:
    print >> sys.stderr, 'usage: python index.py data_dir output_dir' 
    os._exit(-1)

total_file_count = 0
root = sys.argv[1]
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# this is the actual posting lists dictionary
posting_dict = {}
#this is the dictionary storing postings lists file locations during merge
posting_locs = {}
# this is a dict holding document name -> doc_id
doc_id_dict = {}
# this is a dict holding word -> word_id
word_dict = {}
# this is a queue holding block names, later used for merging blocks
block_q = deque([])


def vb_encode_num(num):
  bytes = deque(array('B'))
  while True:
    bytes.appendleft(num % 128)
    if num < 128:
      break
    num = num / 128
  bytes[-1] += 128
  return bytes

def vb_encode(arr):
  bytestream = array('B')
  for num in arr:
    bytes = vb_encode_num(num)
    bytestream.extend(bytes)
  bytestream.append(0); # byte 00000000 never occurs naturally, can be used as a separator
  return bytestream

def vb_decode(bytes):
  numbers = []
  n = 0
  for b in bytes:
    if b < 128:
      n = 128 * n + b
    else:
      n = 128 * n + (b - 128)
      numbers.append(n)
      n = 0

  return numbers

# Convert from an array of docIDs to an array of docDeltas (starting from zero)
def to_gaps(arr):
  gapped = []
  prev = 0
  for n in arr:
    gapped.append(n - prev)
    prev = n
  return gapped


# Convert from an array of docDeltas to an array of docIDs
def from_gaps(arr):
  prev = 0
  ungapped = []
  for n in arr:
    ungapped.append(n + prev)
    prev += n
  return ungapped


# function to count number of files in collection
def count_file():
    global total_file_count # fn called once per file, so just increment counter
    total_file_count += 1
    #print >> sys.stderr, 'you must provide implementation'

# function for printing a line in a postings list to a given file
def print_posting(file, line):
    # a useful function is f.tell(), which gives you the offset from beginning of file
    # you may also want to consider storing the file position and doc frequency in posting_dict in this cal
    word_id = int(line[0])
    count = len(line) - 1
    posting_dict[word_id] = (file.tell(), count)
    gaps = to_gaps(line[1:])
    gaps.insert(0, line[0])
    bytestream = vb_encode(gaps)
    bytestream.tofile(file)
  
def read_posting(file):
    line = []
    currbyte = array('B')
    try:
        currbyte.fromfile(file, 1)
    except EOFError:
        return line
    currint = vb_decode(currbyte)
    while (currbyte.pop() != 0):
        line.append(currint.pop())
        currbyte.fromfile(file, 1)
        currint = vb_decode(currbyte)
    gaps = from_gaps(line[1:])
    gaps.insert(0, line[0]) #worry this is slow operation
    return gaps
  
def pop_left_or_none(d):
    if len(d) < 1:
        return None
    return d.popleft()


    
# function for merging two lines of postings list to create a new line of merged results
def merge_posting (line1, line2):
    # don't forget to return the resulting line at the end
    merge = []
    l1 = deque(line1)
    l2 = deque(line2)
    w1 = pop_left_or_none(l1)
    w2 = pop_left_or_none(l2)
    while True:
        if w1 is None and w2 is None:
            break
        if w1 is None:
            merge.append(w2)
            w2 = pop_left_or_none(l2)
        elif w2 is None:
            merge.append(w1)
            w1 = pop_left_or_none(l1)
        elif int(w1) == int(w2):
            merge.append(w1)
            w1 = pop_left_or_none(l1)
            w2 = pop_left_or_none(l2)
        elif int(w1) < int(w2):
            merge.append(w1)
            w1 = pop_left_or_none(l1)
        else:
            merge.append(w2)
            w2 = pop_left_or_none(l2)
    return merge


doc_id = -1
word_id = 0

for dir in sorted(os.listdir(root)):
    if(dir != '.DS_Store'):
        print >> sys.stderr, 'processing dir: ' + dir
        dir_name = os.path.join(root, dir)
        block_pl_name = out_dir+'/'+dir 
        # append block names to a queue, later used in merging
        block_q.append(dir)
        block_pl = open(block_pl_name, 'w')
        term_doc_list = []
        term_doc_dict = {}
        for f in sorted(os.listdir(dir_name)):
            if(f != '.DS_Store'):
                count_file()
                file_id = os.path.join(dir, f)
                doc_id += 1
                doc_id_dict[file_id] = doc_id
                fullpath = os.path.join(dir_name, f)
                file = open(fullpath, 'r')
                for line in file.readlines():
                    tokens = line.strip().split()
                    for token in tokens:
                        if token not in word_dict:
                            word_dict[token] = word_id
                            word_id += 1
                        if word_dict[token] not in term_doc_dict:
                            term_doc_dict[word_dict[token]] = set([])
                        term_doc_list.append( (word_dict[token], doc_id) )
                        term_doc_dict[word_dict[token]].add(doc_id)
                file.close() #close the file
        print >> sys.stderr, 'sorting term doc list for dir:' + dir
        # sort term doc list
        term_doc_list.sort() # sorts by first tuple item, then second
        # (you need to provide implementation)
        print >> sys.stderr, 'print posting list to disc for dir:' + dir
        # write the posting lists to block_pl for this current block
        for term in sorted(term_doc_dict.keys()):
            line = []
            line.append(int(term))
            docs = sorted(list(term_doc_dict[term]))
            for doc in docs:
                line.append(int(doc))
            print_posting(block_pl, line)
                # (you need to provide implementation)
        block_pl.close()

print >> sys.stderr, '######\nposting list construction finished!\n##########'

print >> sys.stderr, '\nMerging postings...'
while True:
    if len(block_q) <= 1:
        break
    b1 = block_q.popleft()
    b2 = block_q.popleft()
    print >> sys.stderr, 'merging %s and %s' % (b1, b2)
    b1_f = open(out_dir+'/'+b1, 'r')
    b2_f = open(out_dir+'/'+b2, 'r')
    comb = b1+'+'+b2
    comb_f = open(out_dir + '/'+comb, 'w')
    # (provide implementation merging the two blocks of posting lists)
    l1 = read_posting(b1_f)
    l2 = read_posting(b2_f)
    
    while True:
        if not l1 and not l2:
            break
        if not l1:
            print_posting(comb_f, l2)
            l2 = read_posting(b2_f)
        elif not l2:
            print_posting(comb_f, l1)
            l1 = read_posting(b1_f)
        else:
            wid1 = l1[0]
            wid2 = l2[0]
            if wid1 == wid2:
                merge = merge_posting(l1, l2)
                print_posting(comb_f, merge)
                l1 = read_posting(b1_f)
                l2 = read_posting(b2_f)
            elif wid1 < wid2:
                print_posting(comb_f, l1)
                l1 = read_posting(b1_f)
            else:
                print_posting(comb_f, l2)
                l2 = read_posting(b2_f)
    # write the new merged posting lists block to file 'comb_f'
    b1_f.close()
    b2_f.close()
    comb_f.close()
    os.remove(out_dir+'/'+b1)
    os.remove(out_dir+'/'+b2)
    block_q.append(comb)
    
print >> sys.stderr, '\nPosting Lists Merging DONE!'

# rename the final merged block to corpus.index
final_name = block_q.popleft()
os.rename(out_dir+'/'+final_name, out_dir+'/corpus.index')

test = open(out_dir+'/corpus.index', 'r')


# print all the dictionary files
doc_dict_f = open(out_dir + '/doc.dict', 'w')
word_dict_f = open(out_dir + '/word.dict', 'w')
posting_dict_f = open(out_dir + '/posting.dict', 'w')
print >> doc_dict_f, '\n'.join( ['%s\t%d' % (k,v) for (k,v) in sorted(doc_id_dict.iteritems(), key=lambda(k,v):v)])
print >> word_dict_f, '\n'.join( ['%s\t%d' % (k,v) for (k,v) in sorted(word_dict.iteritems(), key=lambda(k,v):v)])
print >> posting_dict_f, '\n'.join(['%s\t%s' % (k,'\t'.join([str(elm) for elm in v])) for (k,v) in sorted(posting_dict.iteritems(), key=lambda(k,v):v)])
doc_dict_f.close()
word_dict_f.close()
posting_dict_f.close()

print total_file_count
