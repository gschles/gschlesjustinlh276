#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re

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
# this is a dict holding document name -> doc_id
doc_id_dict = {}
# this is a dict holding word -> word_id
word_dict = {}
# this is a queue holding block names, later used for merging blocks
block_q = deque([])

# function to count number of files in collection
def count_file():
    global total_file_count # fn called once per file, so just increment counter
    total_file_count += 1
    #print >> sys.stderr, 'you must provide implementation'

# function for printing a line in a postings list to a given file
def print_posting(file, posting_line):
    # a useful function is f.tell(), which gives you the offset from beginning of file
    # you may also want to consider storing the file position and doc frequency in posting_dict in this call
    line = re.split('\s', posting_line.strip())
    word_id = int(line[0])
    count = len(line) - 1
    posting_dict[word_id] = (file.tell(), count)
    file.write(posting_line)
  
def pop_left_or_none(d):
    if len(d) < 1:
        return None
    return d.popleft()

# function for merging two lines of postings list to create a new line of merged results
def merge_posting (line1, line2):
    # don't forget to return the resulting line at the end
    merge = ''
    l1 = deque(line1)
    l2 = deque(line2)
    w1 = pop_left_or_none(l1)
    w2 = pop_left_or_none(l2)
    while True:
        if w1 is None and w2 is None:
            break
        if w1 is None:
            merge += w2 + ' '
            w2 = pop_left_or_none(l2)
        elif w2 is None:
            merge += w1 + ' '
            w1 = pop_left_or_none(l1)
        elif int(w1) == int(w2):
            merge += w1 + ' '
            w1 = pop_left_or_none(l1)
            w2 = pop_left_or_none(l2)
        elif int(w1) < int(w2):
            merge += w1 + ' '
            w1 = pop_left_or_none(l1)
        else:
            merge += w2 + ' '
            w2 = pop_left_or_none(l2)
    return merge.strip() + '\n'


doc_id = -1
word_id = 0

for dir in sorted(os.listdir(root)):
    print >> sys.stderr, 'processing dir: ' + dir
    dir_name = os.path.join(root, dir)
    block_pl_name = out_dir+'/'+dir 
    # append block names to a queue, later used in merging
    block_q.append(dir)
    block_pl = open(block_pl_name, 'w')
    term_doc_list = []
    term_doc_dict = {}
    for f in sorted(os.listdir(dir_name)):
        if str(f) != '.DS_Store':
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
        line = str(term) + ' '
        docs = sorted(list(term_doc_dict[term]))
        for doc in docs:
            line += str(doc) + ' '
        line = line.strip() + '\n'
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
    l1 = b1_f.readline()
    l2 = b2_f.readline()
    while True:
        if l1 == '' and l2 == '':
            break
        if l1 == '':
            print_posting(comb_f, l2)
            l2 = b2_f.readline()
        elif l2 == '':
            print_posting(comb_f, l1)
            l1 = b1_f.readline()
        else:
            line1 = re.split('\s', l1.strip())
            line2 = re.split('\s', l2.strip())
            wid1 = int(line1[0])
            wid2 = int(line2[0])
            if wid1 == wid2:
                merge = merge_posting(line1, line2)
                print_posting(comb_f, merge)
                l1 = b1_f.readline()
                l2 = b2_f.readline()
            elif wid1 < wid2:
                print_posting(comb_f, l1)
                l1 = b1_f.readline()
            else:
                print_posting(comb_f, l2)
                l2 = b2_f.readline()
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
