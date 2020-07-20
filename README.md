# T9, improved

The goal of this project is to find the best cellphone keyboard layout for T9 typing.

Spoiler – the result is:
<table>
  <tr><td>1<br>.,?</td><td>2<br>acky</td><td>3<br>bdfj</td></tr>
  <tr><td>4<br>egm</td><td>5<br>htv</td><td>6<br>ipr</td></tr>
  <tr><td>7<br>lox</td><td>8<br>nqw</td><td>9<br>suz</td></tr>
  <tr><td>*<br>+</td><td>0<br>_</td><td>#<br>⇧</td></tr>
</table>

## Background

This idea was born before we all had smartphones and swipey keyboards and the like: how can we arrange the 26 letters of the alphabet on a cellphone keyboard to make T9-like predictive typing as efficient as possible? In other words, which assignment of 26 letters to eight keys (0 and 1 are non-letter keys) minimizes the number of textonyms – such as, with the standard layout, home, gone, and good?

(Sidenode: I solved this several years ago with IBM CPLEX, which took all but a few seconds to find the optimal key assignment. Now, with a slower machine, access to only open source tools, and an interest in the Minizinc ecosystem, I’m revisiting the problem.)

The answer to the problem will, of course, depend on the word list
from which potential textonyms are drawn. I’ve made my list of
1000 common English words, along with their frequency, available [here](
github.com/skosch/t9_improved). Unfortunately, I don’t remember where I
found it or what corpus I compiled it from.

## Constraints

First, we’ll assemble the constraints we can feed to our solver engine.

Each of the 26 letters will be assigned a key index between 0 and 7 – that’s the output we’re looking for. So we need a 1×26 matrix of integer variables over `{0..7}`, named `letter_keys`. 

In the [Minizinc](https://www.minizinc.org/) language, we can express this as:

```tex
array[1..26] of var 0..7: letter_keys;
```

We channel this into a 26×26 matrix of booleans, `letter_keys_match`, which indicate whether or not any two letters occupy the same key. For instance, if a and b both sit on key number 3, then `letter_keys_match[1, 2] == true`.

Wait – there’s a symmetry here: `letter_keys_match[i, j] == letter_keys_match[j, i]`! Indeed, we can make do with just one triangle of the matrix (let’s use the upper right). Instead of 26×26 = 676 variables, that’s just (26×26 – 26)/2 = 325. It’s a bit annoying having to convert between the two running letter indices of the loop and the one-dimensional index of `letter_keys_match`, but once we work out the arithmetic it’s simple enough:

```tex
array[1..325] of var bool: letter_keys_match;

constraint forall (letter1 in 1..25, letter2 in (letter1+1)..26) (
  let {
    % convert from 2d alphabet index (upper right triangle) to 1d index
    int: index = 26 * (letter1 - 1) + letter2 - letter1 - (letter1*letter1 - letter1) div 2
  } in 
  letter_keys_match[index] = (letter_keys[letter1] == letter_keys[letter2])
);
```

Let’s now get to the optimization part. To quantify how bad a solution is, we need to look at all word pairs where:

* both words have the same length, and
* for each letter of the first word, the corresponding letter of the second word sits on the same key (given whatever `letter_keys` will be).

For each one of these word pairs, let’s come up with a number – a “badness value” – that represents how inconvenient it would be to have the pair be a textonym. Something like `min(10000/frequency1, 10000/frequency2)` works well: the frequency of the less-used word determines the degree of annoyance. (There’s nothing wrong with `1.0/frequency`, but most finite domain solvers work with integers only, so we need bigger numbers.) If, for example, we end up with a layout in which *the* is a textonym with *fix*, then that’s not too terrible: having to manually choose *fix* over *the* will happen relatively rarely, because *fix* is itself a relatively rare word. A conflict between *the* and *and*, however, would be seriously annoying, because *and* comes up so often.

Our word list contains 76436 pairs of equal-length words (finding this number shall be an exercise for the reader). So let’s create:

```tex
array[1..76436] of var float: pair_badness;
```

along with the 76436 Minizinc constraints, one per pair. They should all look somewhat like this:

```tex
constraint pair_badness[43] = if letter_keys_match[14,14]+letter_keys_match[5,7] == 2 then 11 else 0 endif;
```

## More constraints
There is more we can do. First off, each key should accommodate three or four letters:

```tex
constraint global_cardinality_low_up(letter_keys, [0, 1, 2, 3, 4, 5, 6, 7], [3, 3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4, 4]);
```

Then, we can observe that the positions of any two keys can be swapped, without affecting the quality of the solution at all. To exclude those symmetries, we’ll require that the keys be sorted by the first of their respective letters. In other words: letter a must be on key 0; letter b must be on key 0 or 1 (but not 2), etc.:

```tex
constraint forall (letter in 2..26) (
  let {
    var int: maxkey = max([letter_keys[k] | k in 1..(letter-1)]),
  } in 
  letter_keys[letter] <= maxkey + 1
);
```

And to explicitly strengthen this constraint, we can write for the first eight letters:

```tex
constraint forall (key in 1..8) (
  letter_keys[key] <= key - 1
);
```

Finally, we can pre-prune our search tree by stating a priori which letters we definitely don’t want on the same key. This information is easily found: just look at the most frequent word pairs with a letter-distance of one. For instance, you certainly won’t want *he* and *me* to be textonyms, so as potential key-mates the letters *h* and *m* are out from the start. Similarly, each vowel *aeiou* should most definitely get its own key. We can write down a bunch of common ones:

```tex
constraint all_different([letter_keys[k] | k in {1,5,9,15,21}]); % aeiou
constraint all_different([letter_keys[k] | k in {7,12}]);  % gl
constraint all_different([letter_keys[k] | k in {13,12}]); % ml
constraint all_different([letter_keys[k] | k in {13,8}]);  % etc...
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
```

The more we add, the smaller the search tree, and the faster the solving process. On the other hand, if we exclude too many solutions, we might miss the optimal one – or end up finding none at all.

## Solution

Finally, we’ll add

```tex
solve minimize sum(pair_badness);
output([show(letter_keys)]);
```

and we’re on our way!

On my (admittedly slow) laptop, the conversion from Minizinc to Flatzinc takes about two minutes when targeting Google OR-tools, and the resulting Flatzinc file weighs about 62MB.

I started OR-tools and went for a run. When I came back, it had found the optimal key assignment with a total badness of 149: 

```tex
letter_keys = array1d(1..26, [0, 1, 0, 1, 2, 1, 2, 3, 4, 1, 0, 5, 2, 6, 5, 4, 6, 4, 7, 3, 7, 3, 6, 5, 0, 7]);
```

which corresponds to

```
acky  bdfj  egm  htv  ipr  lox  nqw  suz
```

– so there you go; the least annoying T9 keyboard for Simple English!

Our layout still suffers from nine textonyms:

```
32  its    its    #  LOL,  I  guess  this  one's  unavoidable
26  told   hold
19  along  alone
14  wife   wide
13  are    arm
13  fire   firm
11  here   term
11  fall   ball
10  from   film
```

But that’s nothing compared to the traditional alphabetic ordering, which has 46 textonyms for a total badness of 1998:

```
222  he       if
222  on       no
153  there    these
144  them     then
121  of       me
103  in       go
93   or       mr
90   up       us
62   good     home
50   was      war
45   might    night
34   line     kind
33   work     york
32   its      its
31   have     gave
30   any      boy
30   seem     seen
29   an       am
28   go       im
28   in       im
27   part     past
25   say      pay
22   but      cut
22   case     care
21   they     view
20   good     gone
20   home     gone
20   room     soon
18   see      red
17   move     note
16   done     food
16   find     fine
14   hand     game
14   said     paid
14   wall     walk
14   wife     wide
13   dont     foot
13   got      hot
13   law      lay
12   alone    blood
12   bed      add
11   call     ball
11   needs    offer
11   purpose  suppose
11   reason   season
11   run      sun
```

Man, remember on/no and of/me? I always hated those two.


## Running
To run this, simply download it and run
```
python constraints.py
```
which will generate a file `constraints.mzn` in the same directory. Convert this file to Flatzinc format via the `mzn2fzn` compiler provided with [libminizinc](https://github.com/MiniZinc/libminizinc), and pass the output to your favourite solver.
