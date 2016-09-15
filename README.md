# T9^improved
Find the best possible T9 keyboard layout given a word list by minimizing the total annoyance introduced by textonyms.

For more info, read the blog entry at www.aldusleaf.org.

## Running
To run this, simply download it and run
```
python constraints.py
```
which will generate a file `constraints.mzn` in the same directory. Convert this file to Flatzinc format via the `mzn2fzn` compiler provided with [libminizinc](https://github.com/MiniZinc/libminizinc), and pass the output to your favourite solver.
