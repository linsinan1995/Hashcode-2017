# Hashcode 2017 Qualification round solution

# Greedy 1
simple greedy solution => put most frequent requested video to the most low-latency cache

result:
```
me_at_the_zoo.in               => 434442
videos_worth_spreading.in      => 481540
trending_today.in              => 499981
kittens.in.txt                 => 563313
==========================================================
TOTAL SCORE: 1979276
==========================================================
```

rank at 702 nd according to https://bytefreaks.net/google/google-hash-code-2017-results

# Greedy 2

simple greedy solution => put larget total direct request-time video(number of requests * data center latency) to the most low-latency cache


result:
```
me_at_the_zoo.in               => 465350
videos_worth_spreading.in      => 476642
trending_today.in              => 499981
kittens.in.txt                 => 611227
==========================================================
TOTAL SCORE: 2053200
==========================================================
```

rank at 566 th

## Merge best results from greedy 1
use result of videos_worth_spreading.in from greedy 1
```
TOTAL SCORE: 2058098
```

rank at 552 nd