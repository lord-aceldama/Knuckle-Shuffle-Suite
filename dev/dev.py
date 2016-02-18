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
import cmdargs, version, shuffle#, abacus


#-- Global Constants
VERSION = version.Version("Knuckle-Shuffle", 0, 9, 0)


#=========================================================================================================[ METHODS ]==
def show_version():
    """ Shows the script version. """
    print "\033[1;32;40m{0}\n".format(str(VERSION))
    

def show_help():
    """ Shows the command-line help. """
    print "\033[1;32;40mhep!!\n"


def startup():
    """ Interprets command-line options and executes script accordingly.
    """
    #-- Get command-line options.
    arg = cmdargs.CmdArgs(("-c", "--charset"), (int, "-l", "--length"), ("-s", "--start"), ("-h", "--help"),
                          ("-v", "--version"))
    
    #-- See what to do with them.
    if arg.isset("--version"):
        #-- Version requested
        show_version()
    elif arg.isset("--charset", "--length") and (len(arg.value("-c")) * arg.value("-l") > 0):
        #-- Check for correct usage
        fail = arg.isset("--help")
        if fail:
            #-- Incorrect/insuficient parameters given.
            show_help()
        else:
            #-- Minimum requirements met.
            print arg.isset("--charset", "--length"), arg.type("-c"), arg.type("-l")
    else:
        #-- Incorrect/insuficient parameters given.
        show_help()


#============================================================================================================[ MAIN ]==
startup()
