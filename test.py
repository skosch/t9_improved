f = open('./1-1000.txt', 'r')
freq_words = f.read().splitlines()
f.close()

frequencies = list(map(lambda x: int(x.split(',')[0]), freq_words))
words = list(map(lambda x: x.split(',')[1], freq_words))
       #a b c d e f g h i j k l m n o p q r s t u v w x y z
keys = [0,6,7,0,1,0,1,3,5,2,5,7,1,4,7,5,6,6,2,3,2,3,4,3,5,4] # 254 (best so far)
# adf brq clo egm htvx ikpy nwz jsu

# obviously, all_different(a, e, i, o, u)
      # a  b  c  d  e  f  g  h  i  j  k  l  m  n  o  p  q  r  s  t  u  v  w  x  y  z
      # 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
keys =[0, 1, 0, 1, 2, 1, 2, 3, 4, 1, 0, 5, 2, 6, 5, 4, 6, 4, 7, 3, 7, 3, 6, 5, 0, 7] 
#keys = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7, 7, 7]

# problem pairs: gl, ml, mh, aeiou, gh, mn, ps, rs, no, ig, om, fe, re


matchcount = 0
totalbadness = 0
for w1 in range(len(words) - 1):
    for w2 in range(w1 + 1, len(words)):
        if (len(words[w1]) != len(words[w2])):
            continue
        matches = [keys[ord(l1) - 97] == keys[ord(l2) - 97] for (l1, l2) in zip(words[w1], words[w2])]
        if all(matches):
            badness = min(int(10000/frequencies[w1]), int(10000/frequencies[w2]))
            matchcount += 1
            totalbadness += badness
            print(badness, words[w1], words[w2])

print("Total:", matchcount, ", badness:", totalbadness)


