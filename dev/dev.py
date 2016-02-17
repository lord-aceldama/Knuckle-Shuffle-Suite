#!/usr/bin/env python

""" Knuckle Shuffle
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel

    -----------------

    UNDER CONSTRUCTION: so many things to do still...
"""

#-- Dependencies
#import sys, math
import cmdargs#, abacus, shuffle


#-- Global Constants
#[None]

#=========================================================================================================[ METHODS ]==
def show_help():
    """ Shows the command-line help. """
    print "hep!!"

def startup():
    """ X """
    args = cmdargs.CmdArgs(("-c", "--charset"), (int, "-l", "--length"), ("-s", "--start"), ("-h", "--help"))
    if not args.isset("--help"):
        if args.isset("--charset", "--length") and (len(args.value("-c")) * args.value("-l") > 0):
            #-- Minimum Requirements
            print args.isset("--charset", "--length"), args.type("-c"), args.type("-l")
        else:
            show_help()
    else:
        show_help()


#============================================================================================================[ MAIN ]==
startup()
