import sys
import itertools

f1 = open(sys.argv[1], 'r')
f2 = open('data/gold.txt', 'r')

right = 0
total = 0
for pair in itertools.izip(f1.readlines(), f2.readlines()):
  total += 1
  if pair[0] == pair[1]:
    right += 1
  else:
    print pair[0].strip()
print >> sys.stderr, right, total, "acc = ", 100*float(right)/total