###THE THEORY:
The Abacus class is designed to break a large keyspace into smaller chunks. When you 
consider the traditional incremental brute-force algoritm, it's clear  to see that 
keys starting with larger characters render incremental searches inefficient.


###FOR EXAMPLE:
Consider the keyspace [0-9a-f] when the 4-character key is "dacb" Abacus will scan 
permutations in keyspace as [0123------------], [1234, 2345, 3456, 4567, 5678, 6789, 
789a, 89ab, 9abc] and [----------abcd--] which means that the key will be discovered 
in under 2'176 keys. (4^4 + 10 \* (4^4 - 4^3)) In fact, having piped Abacus' output 
through **grep -n "dacb"**, it showed that the token was found on line 1'897 which 
is a vast improvement over 56'011 (of 65'536) keys had .


###PITFALLS:
Of course this method is not fool-proof. If we consider the keyspace we used in the
example and "fed0" was the key, the entire keyspace would need to be scanned (as if 
"ffff" were the key used in an incremental search). When you take a normal (random)
distribution like a key generated by router manufacturers, _\*cough\* for educational 
purposes only \*cough\*_ it can be seen by looking at the curve on a graph that having
both the 1st and last chars  in the keyspace is somewhat unlikely if the key's length
is between 0 and 25% of the character space. Both the script and its output can be 
found in the \[[research directory](https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/tree/master/research)]. 
The following is an excerpt and was generated by calculating the distance between the 
max and min characters of a random 5 character hex key over 10'000'000 iterations 
(ie. dacfb: f - a = 5 etc.):
        
                     Montecarlo Generated Graph:

         20.0 |                                  *  *          
        19.99 |                               *  *  *          
        19.99 |                               *  *  *          
        19.98 |                            *  *  *  *  *       
        19.97 |                            *  *  *  *  *       
        19.96 |                            *  *  *  *  *       
        19.96 |                         *  *  *  *  *  *       
        19.95 |                         *  *  *  *  *  *       
        19.94 |                         *  *  *  *  *  *       
        19.94 |                      *  *  *  *  *  *  *  *    
        19.93 |                      *  *  *  *  *  *  *  *    
        19.92 |                      *  *  *  *  *  *  *  *    
        19.92 |                   *  *  *  *  *  *  *  *  *    
        19.91 |                   *  *  *  *  *  *  *  *  *    
         19.9 |                   *  *  *  *  *  *  *  *  *    
        19.89 |                *  *  *  *  *  *  *  *  *  *    
        19.89 |                *  *  *  *  *  *  *  *  *  *    
        19.88 |             *  *  *  *  *  *  *  *  *  *  *    
        19.87 |          *  *  *  *  *  *  *  *  *  *  *  *    
        19.87 +-*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-
                0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f

That being said,  there's always a chance that the full  65'536  keys may need to be
checked when brute-forcing a 4-digit hex key.