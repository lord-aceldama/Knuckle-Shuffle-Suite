### THE THEORY:
Knuckle-shuffle is designed to improve on existing incremental brute-force algorithms.
When you consider the traditional incremental brute-force algoritm, it's clear to see
that keys starting with larger characters render incremental searches inefficient. It 
is more likely that a randomly generated passcode will have two similar characters that
are separated by other characters rather than all the same characters neatly grouped 
together.


### HOW IT WORKS:
Instead of incrementing the key step by step, knuckle-shuffle processes all pemutations
of a key. When a random hex key is generated, chances are better that characters are not 
in ascending order, which would be found efficiently by traditional brute-force algorithms, 
but rather in random order. What knuckle-shuffle does is increment the key and tries all 
permutations of that key.


### FOR EXAMPLE:
Consider the keyspace [0-9a-f] when the hexadecimal key is "c0de1337". A traditional 
brute-force algorithm would have to run through 3'235'779'384 of 4'294'967'296 keys
before succeeding, whereas knuckle-shuffle would find it among the permutations in
"01337cde". Unfortunately I don't have an exact number, but permutations per key can
be calculated by length/a!b!...n! where a, b ... n is the number of repeated characters
in a key. So if the key is aaabbccd then the permutation formula is 8!/(3!2!2!1!) for a 
total of 1'680 keys.


### PITFALLS:
Of course this method (as with any brute force algorithm) is not fool-proof. You may still
have to go through the entire keyspace if the password were "ffffffff", but at least 
because of the smart_inc method, you won't have any duplicate scans.

