###THE KNUCKLE-SHUFFLE SUITE:
Well, what can i say - if you have time on your hands...  
...The knuckle-shuffle suite is designed to be a more efficient way of brute-forcing a 
keyspace. It consists of the following scripts:
* __knuckleshuffle.py:__ The main script. It sends the generated keys to STDOUT and messages to STDERR.
* __sausage-fest.py:__ (Future code) Will be the server script for cloud cracking should you have
  two or more slaves a-shufflin'.
* __abacus.py:__ Will eventually be incorporated into knuckle-shuffle and sausage-fest. It's basically
  just here as a development script so i can experiment and develop the concept without altering the 
  future host. 

###LICENSE:
Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
available \[[here](http://www.gnu.org/licenses/gpl-2.0.txt)].  

By using these scripts you agree that it is for intellectual purposes only, unless you own 
whatever you're brute-forcing and/or obtained it with the legal owner's permission.  
  
(C) 2015 David A Swanepoel


###REQUREMENTS:
The knuckle-shuffle suite was designed for use with Python 2.7.1 on Linux.


###SCRIPTS:
####knuckle-shuffle.py
**Theory:** The theory behind how and why this script can be found \[[here](https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/knuckle-shuffle.md)].  
  
**Usage:** knuckle-shuffle.py -l=N -l=CHARS \[-s=START]
 * -l=N where N is the length of the key
 * -l=CHARS where CHARS is a string of characters signifying the keyspace
 * -s=START where START is the start hash 

**Examples:** 
  * knuckle-shuffle.py -l=3 -c=0123456789
  * knuckle-shuffle.py -l=8 -c=abcdefghjklmnpqrstuvwxyz -s=$(grep -Po "^\w+" sess.txt)

####sausage-fest.py
**Theory:** *[ToDo]*  
  
**Usage:** *[ToDo]*  

####abacus.py
**Theory:** The theory behind how and why this script can be found \[[here](https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/abacus.md)].  
  
**Usage:** *[ToDo]*


###INSTALLATION:
Although installation is not strictly necessary, it certainly makes it easier if you copy the scripts 
into the /usr/bin. I'll be sure to get back to this section once i have more than just knuckle-shuffle.py
working.
