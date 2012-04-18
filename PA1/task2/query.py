#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re
from array import array

if len(sys.argv) != 2:
    print >> sys.stderr, 'usage: python query.py index_dir' 
    os._exit(-1)

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

# Convert from an array of docDeltas to an array of docIDs
def from_gaps(arr):
  prev = 0
  ungapped = []
  for n in arr:
    ungapped.append(n + prev)
    prev += n
  return ungapped


  
def read_compressed_posting(file):
    line = array('B')
    currbyte = array('B')
    try:
        currbyte.fromfile(file, 1)
    except EOFError:
        return line
    while True:
        if currbyte.count(0) == 1:
            currbyte.fromfile(file,1)
            if currbyte.count(0) == 2:
                currbyte.fromfile(file,1)
                if currbyte.count(0) == 3:
                    break
        line.extend(currbyte)
        currbyte = array('B')
        currbyte.fromfile(file,1)  
    line = vb_decode(line)             
    gaps = from_gaps(line[1:])
    gaps.insert(0, line[0]) #worry this is slow operation
    return gaps


def merge_posting (p1, p2):
    new_posting = []
    # provide implementation for merging two postings lists
    i = 0
    j = 0
    while True:
        if i >= len(p1) or j >= len(p2):
            break
        if int(p1[i]) == int(p2[j]):
            new_posting.append(p1[i])
            i += 1
            j += 1
        elif int(p2[j]) < int(p1[i]):
            j += 1
        else:
            i += 1             
    return new_posting

# file locate of all the index related files
index_dir = sys.argv[1]
index_f = open(index_dir+'/corpus.index', 'r')
word_dict_f = open(index_dir+'/word.dict', 'r')
doc_dict_f = open(index_dir+'/doc.dict', 'r')
posting_dict_f = open(index_dir+'/posting.dict', 'r')

word_dict = {}
doc_id_dict = {}
file_pos_dict = {}
doc_freq_dict = {}

print >> sys.stderr, 'loading word dict'
for line in word_dict_f.readlines():
    parts = line.split('\t')
    word_dict[parts[0]] = int(parts[1])
print >> sys.stderr, 'loading doc dict'
for line in doc_dict_f.readlines():
    parts = line.split('\t')
    doc_id_dict[int(parts[1])] = parts[0]
print >> sys.stderr, 'loading index'
for line in posting_dict_f.readlines():
    parts = line.split('\t')
    term_id = int(parts[0])
    file_pos = int(parts[1])
    doc_freq = int(parts[2])
    file_pos_dict[term_id] = file_pos
    doc_freq_dict[term_id] = doc_freq


def read_posting(term_id):
    # provide implementation for posting list lookup for a given term
    # a useful function to use is index_f.seek(file_pos), which does a disc seek to 
    # a position offset 'file_pos' from the beginning of the file
    global index_f
    file_pos = file_pos_dict[term_id]
    index_f.seek(file_pos)
    posting_list = read_compressed_posting(index_f)
    posting_list = posting_list[1:]
    return posting_list

# read query from stdin
while True:
    input = sys.stdin.readline()
    input = input.strip()
    if len(input) == 0: # end of file reached
        break
    input_parts = input.split()
    # you need to translate words into word_ids
    # don't forget to handle the case where query contains unseen words
    # next retrieve the postings list of each query term, and merge the posting lists
    # to produce the final result
    #print >> sys.stderr, input_parts
    word_ids = []
    for term in input_parts:
        if term in word_dict:
            word_id = word_dict[term]
            word_ids.append((word_id, doc_freq_dict[word_id]))
        else:
            print 'no results found'
            os._exit(0)
    word_ids = sorted(word_ids, key=lambda w: w[1])
    
    posting = read_posting(word_ids[0][0])
    for i in range(1,len(word_ids)):
        next_posting = read_posting(word_ids[i][0])
        posting = merge_posting(posting, next_posting)
    if not posting:
        print 'no results found'
    else:
        docs = []
        for d in posting:
            docs.append(doc_id_dict[int(d)])
        docs.sort()
        for d in docs:
            print d
        
    # don't forget to convert doc_id back to doc_name, and sort in lexicographical order
    # before printing out to stdout
