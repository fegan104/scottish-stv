## Scottish STV

A python implementation of Scottish Single Transferable Vote based on the process described by [OpaVote](https://blog.opavote.com/2016/11/plain-english-explanation-of-scottish.html).


## Usage

`rcv.py [-h] [-f FILE] [-n NUM_WINNERS]`

Administer election.

arguments:
  - -h, --help
    - show this help message and exit
  - -f FILE, --file FILE 
    - Name of the election results file
  - -n NUM_WINNERS, --num_winners NUM_WINNERS
    - Number of winners to pick

## Elections File

The structure of the data must be a csv file in the form of:

```
   Alice  ,    Bill   , Chelsea
1st Choice, 3rd Choice, 2nd Choice
1st Choice, 2nd Choice,
2nd Choice, 1st Choice, 3rd Choice
          , 1st Choice,
          ,           , 1st Choice
```