def get_index(l1, l2):
    first = min(l1, l2)
    second = max(l1, l2)
    return str(int( 26*(first-1) + second - first - (first**2-first)/2 ))

f = open('./1-1000.txt', 'r')
freq_words = f.read().splitlines()
f.close()

frequencies = list(map(lambda x: int(x.split(',')[0]), freq_words))
words = list(map(lambda x: x.split(',')[1], freq_words))
constraints = []
index = 0
for i in range(0, len(words) - 1):
    # go through the letters of the words
    first_word_letters = [ord(words[i][l]) - 97 for l in
            range(len(words[i]))]

    first_word_badness = 10000/frequencies[i]

    for j in range(i + 1, len(words)):
        if len(words[i]) != len(words[j]):
            continue
        # we could totally memoize the below, but whatever
        second_word_letters = [ord(words[j][l]) - 97 for l in
                range(len(words[j]))]
        second_word_badness = 10000/frequencies[j]
        
        match_summands = [("letter_keys_match[" + get_index(fwli + 1, swli + 1)
            + "]") if fwli != swli else "1" for (fwli, swli) in zip(first_word_letters,
                    second_word_letters)]

        badness = min(first_word_badness, second_word_badness)

        constraint_string = ("constraint pair_badness[" + str(index + 1) + "] = if " + "+".join(match_summands) + " == " + \
                        str(len(first_word_letters)) + " then " + str(int(badness)) + " else 0 endif;")

        constraints.append(constraint_string)
        index += 1

f = open('./constraints.mzn', 'w')

f.write("""include "globals.mzn";
array[1..26] of var 0..7: letter_keys;
array[1..325] of var bool: letter_keys_match;
array[1.."""+str(index)+"""] of var 0..10000: pair_badness;

constraint forall (letter1 in 1..25, letter2 in (letter1+1)..26) (
  let {
    int: index = 26 * (letter1 - 1) + letter2 - letter1 - (letter1*letter1 - letter1) div 2   % convert from 2d alphabet index (upper right triangle) to 1d index
  } in 
  letter_keys_match[index] = (letter_keys[letter1] == letter_keys[letter2])
);

constraint global_cardinality_low_up(letter_keys, [0, 1, 2, 3, 4, 5, 6, 7],
[3, 3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4, 4]);

constraint forall (letter in 1..8) (
  letter_keys[letter] <= letter - 1
);

constraint all_different([letter_keys[k] | k in {1,5,9,15,21}]);
constraint all_different([letter_keys[k] | k in {7,12}]);  % gl
constraint all_different([letter_keys[k] | k in {13,12}]); % ml
constraint all_different([letter_keys[k] | k in {13,8}]); 
constraint all_different([letter_keys[k] | k in {7,8}]); 
constraint all_different([letter_keys[k] | k in {13,14}]); 
constraint all_different([letter_keys[k] | k in {16,19}]); 
constraint all_different([letter_keys[k] | k in {18,19}]); 
constraint all_different([letter_keys[k] | k in {14,15}]); 
constraint all_different([letter_keys[k] | k in {7,9}]); 
constraint all_different([letter_keys[k] | k in {5,6}]); 
constraint all_different([letter_keys[k] | k in {5,18}]); 
constraint all_different([letter_keys[k] | k in {12,20}]); 
constraint all_different([letter_keys[k] | k in {7,19}]); 
constraint all_different([letter_keys[k] | k in {6,20}]); 
constraint all_different([letter_keys[k] | k in {13,18}]); 

constraint forall (letter in 2..26) (
  let {
    var int: maxkey = max([letter_keys[k] | k in 1..(letter-1)]),
  } in 
  letter_keys[letter] <= maxkey + 1
);

solve minimize sum(pair_badness); % :: bool_search(letter_keys_match, occurrence, indomain_min, complete);
output([show(letter_keys)]);
""")

f.write("\n".join(constraints))
f.close()
