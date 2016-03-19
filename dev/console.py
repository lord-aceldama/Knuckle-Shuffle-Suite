""" CONSOLE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import os, sys, time, random


#=============================================================================================[ BASIC CONSOLE CLASS ]==
class Basic(object):
    """ A basic console control class. Includes caret positioning and output manipulation.
            EXPOSES:
                Constants:
                    [None]
                
                Properties:
                    (ro) [bool] is_linux        : Returns True if os platform is Linux.
                    (ro) [bool] is_windows      : Returns True if os platform is Windows.
                    (ro) [bool] ansi_support    : Returns True if stdout supports ansi.
                
                Functions:
                    [None]
                
                Methods:
                    cls()           : 
                    clreol()        : 
                    home()          : 
                    gotoxy(x, y)    : 
                    write(*arg)     : 
                    writeln(*arg)   : 
            
            RESEARCH:
                - https://docs.python.org/2/library/os.html#os.isatty
                - https://docs.python.org/2/library/sys.html#sys.platform
                - https://en.wikipedia.org/wiki/ANSI_escape_code
                - https://rosettacode.org/wiki/Terminal_control/Cursor_positioning#Python
    """
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _stdout = None
    _stderr = None
    _stdtty = False
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        """ Initialises the class.
        """
        #-- Set output vectors
        self._stderr = stderr if type(stderr) == file else None
        self._stdout = stdout if type(stdout) == file else None
        assert self._stdout is not None, "FATAL: Primary output must be a valid file handle or pipe."
        self._stdtty = os.isatty(self._stdout.fileno())
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @staticmethod
    @property
    def is_linux():
        """ Returns True if python is running on Linux. """
        return sys.platform.startswith('linux')
    
    
    @staticmethod
    @property
    def is_windows():
        """ Returns True if python is running on Windows. """
        return sys.platform.startswith('win')
    
    
    @property
    def ansi_support(self):
        """ Returns True if primary output is a TTY and os is not windows. """
        return self._stdtty and not self.is_windows
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _write(self, arg_list, linefeed):
        """ Tries to write to primary output. If an error occurs, it writes the error to the secondary output. 
        """
        if self._stdout is not None:
            parsed = " ".join([str(item) for item in arg_list])
            try:
                self._stdout.write(parsed + ("\n" if linefeed else ""))
                self._stdout.flush()
            except Exception as err:
                self._error(str(err))
        else:
            self._error("Output not set or invalid")
    
    
    def _error(self, message):
        """ Tries to write to secondary output. If _stderr is None, no output gets written. If an error occurs and 
            _stderr is not None, a fatal exception is raised and the program terminates.
        """
        if self._stderr is not None:
            try:
                self._stderr.write("ERROR: {0}.\n".format(message))
                self._stderr.flush()
            except Exception as err:
                raise Exception("FATAL: {0}.".format(str(err)))
    
    
    def _ansi(self, code, *args):
        """ Returns the ansi escape sequence if the console supports it, or raises an error and returns an empty string
            if it doesn't.
        """
        result = ""
        if self.ansi_support:
            result = "\x1b[{0}{1}".format(";".join([str(arg) for arg in args]) if type(args) == list else "", code)
        else:
            self._error("Primary output does not support ansi")
        return result
        
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def cls(self):
        """ Clears the screen and resets the cursor to position (0; 0).
        """
        self.write(self._ansi("J", 2))
        self.gotoxy(0, 0)
    
    
    def clreol(self):
        """ Attempts to write the clreol ansi escape sequence to the console.
        """
        self.write(self._ansi("K"))
    
    
    def home(self):
        """ Writes the carriage return string literal to the primary output if it is a tty or raises an error and does
            nothing if it doesn't.
        """
        if self._stdtty:
            self.write("\r")
        else:
            self._error("Primary output is not a tty")
    
    
    def gotoxy(self, x, y):
        """ Moves the carriage to position (x; y).
        """
        self.write(self._ansi("H", y, x))
    
    
    def write(self, *args):
        """ Writes to the primary output.
        """
        self._write(list(args), False)
    
    
    def writeln(self, *args):
        """ Like writeln, but adds an line-feed character to the end.
        """
        self._write(list(args), True)


#=============================================================================================[ COLOR CONSOLE CLASS ]==
class Color(Basic):
    """ An expansion on the basic console class. Includes color ansi escape sequences. """


#===================================================================================================[ CONSOLE CLASS ]==
class ConsoleX(object):
    """ Class to extend and simplify common console output like colour and font settings or dimension retrieval.
            EXPOSES:
                Constants:
                    COLOR
                    STYLE
                
                Properties:
                    (ro) [int] width            : Returns application's major version.
                    (ro) [int] height           : Returns application's minor version.
                    (ro) [int] color            : Returns application's minor version.
                    (ro) [int] backgroundcolor  : Returns application's minor version.
                    (rw) [bool] bright          : Gets or sets the current bright style setting.
                    (rw) [bool] underline       : Gets or sets the current underline style setting.
                    
                Methods:
                    cls()                       : Clears the screen.
                    reset()                     : Resets color and style to the default without clearing screen.
                    gotoxy(pos_x, pos_y)        : Moves the cursor to position XY.
                    setcolor(color)             : Sets the foreground color. Color can be either a string or a number.
                    setbackgroundcolor(color)   : Sets the background color. Color can be either a string or a number.
                    check_size()                : Forces a re-check of the window width and height.
                    write(text)                 : Writes the text to the console.
                    writeln(text)               : Same as write() with a newline.
            
            RESEARCH:
                - https://en.wikipedia.org/wiki/ANSI_escape_code
                - http://ozzmaker.com/add-colour-to-text-in-python/
                - https://rosettacode.org/wiki/Terminal_control/Cursor_positioning#Python
                - http://coolmaxhot.com/graphics/hex-color-palette.htm
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    _DEFAULTS   = [0, 0, False, False]
    _WH_RECHECK = 5 #-- Recheck width/height every N seconds.
    
    COLOR = [ "system", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "black" ]
    STYLE = [ "none", "bright", "underline" ]
    
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _output = sys.stdout
    _color  = { "f" : 0, "b" : 0 }
    _style  = { "b" : False, "u" : False }
    
    _wht = 0
    _wh  = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, output = sys.stdout):
        """ Initializes the object.
        """
        self._output = output
        self.reset()
        self._win_wh()
    
    
    def __str__(self):
        """ Returns a string representation of the the object.
        """
        result = "[CONSOLE FG:{0} BG:{1} STYLE:".format(self.COLOR[self._color["f"] - 30],
                                                        self.COLOR[self._color["b"] - 40])
        if not (self._style["b"] or self._style["u"]):
            result += self.STYLE[0]
        else:
            if self._style["b"]:
                result += self.STYLE[1]
            if self._style["u"]:
                result += "{0}{1}".format(("" if not self._style["b"] else ", "), self.STYLE[2])
        result += "]"
        return result
        
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def width(self):
        """ Returns the console width. """
        return self._win_wh()[0]
    
    
    @property
    def height(self):
        """ Returns the console height. """
        return self._win_wh()[1]
    
    
    @property
    def color(self):
        """ Returns the current text color. """
        return self._getcolorname(self._color["f"])
    
    
    @property
    def backgroundcolor(self):
        """ Returns the current text background color. """
        return self._getcolorname(self._color["b"])
    
    
    @property
    def bright(self):
        """ Returns the current text background color. """
        return self._style["b"]
    @bright.setter
    def bright(self, value):
        """ Sets bright and style-update flags. """
        self._setstyle("b", value)
    
    
    @property
    def underline(self):
        """ Returns the current text background color. """
        return self._style["u"]
    @underline.setter
    def underline(self, value):
        """ Sets underline and style-update flags """
        self._setstyle("u", value)
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    @staticmethod
    def _restrain(value, vmin, vmax):
        """ Restrains a number to a certain range. """
        return max(vmin, min(vmax, value))
    
    
    def _win_wh(self):
        """ Returns the console window height and width as a list of int. """
        if self._wht < time.time():
            self._wht = time.time() + self._WH_RECHECK
            self._wh = [int(x) for x in os.popen('stty size', 'r').read().split()]
        return self._wh
    
    
    def _setstyle(self, key, value):
        """ Clean up property setters. """
        if (type(value) == bool) and (self._style[key] != value):
            self._style[key] = value
    
    
    def _getcolor(self, color):
        """ Translates user defined color to usable color. """
        result = None
        if (type(color) == int) and (color >= 0) and (color < len(self.COLOR)):
            result = color
        elif type(color) == str:
            cleaned = color.strip().lower()
            if cleaned in self.COLOR:
                result = self.COLOR.index(cleaned)
        assert (result is not None), "Bad color"
        return result
    
    
    def _getcolorname(self, color_code):
        """ Translates a color to color name"""
        result = color_code % 10
        return self.COLOR[result]
    
    
    def _format(self, text):
        """ Returns a formatting string that sets the current console state. """
        style = (("m\033[1" if self.bright else "") + 
                 ("m\033[4" if self.underline else ""))
        color = ((";{0}".format(self._color["f"]) if self.color != "system" else "") + 
                 (";{0}".format(self._color["b"]) if self.backgroundcolor != "system" else ""))
        return "\033[0{0}{1}m{2}\033[0m".format(style, color, text)
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    @staticmethod
    def cls():
        """ Clears the console but does not alter colors and styles. """
        os.system('cls' if os.name=='nt' else 'clear')
    
    
    def reset(self):
        """ Resets colours and styles to their default values without clearing the console. """
        self.setcolor(self._DEFAULTS[0])
        self.setbackgroundcolor(self._DEFAULTS[1])
        self.bright = self._DEFAULTS[2]
        self.underline = self._DEFAULTS[3]
        self.write("")
    
    
    def gotoxy(self, pos_x, pos_y):
        """ Moves the cursor to console X and Y. """
        win_wh = self._win_wh()
        self.write("\033[{0};{1}H".format(self._restrain(pos_x, 0, win_wh[0]), self._restrain(pos_y, 0, win_wh[1])))
    
    
    def setcolor(self, color):
        """ Sets the console forecolor. """
        self._color["f"] = 30 + self._getcolor(color)
            
    
    def setbackgroundcolor(self, color):
        """ Sets the console's background color. """
        self._color["b"] = 40 + self._getcolor(color)
    
    
    def check_size(self):
        """ Forces a re-check of the console width and height. """
        self._wht = 0
        self._win_wh()
    
    
    def write(self, text):
        """ Writes text to the console. """
        self._output.write(self._format(text))
        self._output.flush()
        
    
    def writeln(self, text):
        """ Writes text to the console and adds a newline. """
        self._output.write(self._format(text) + "\n")


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
    print "1234\rabc\x1b[Kz"
    with open('setup.txt', "w+") as fobj:
        print type(fobj)
    print type(sys.stdout), os.isatty(sys.stdout.fileno())
    print type(sys.stderr), os.isatty(sys.stderr.fileno())
    print "os:", sys.platform
    exit()
    
    test = ConsoleX()
    test.cls()
    for _ in xrange(500):
        test.gotoxy(random.randrange(test.width + 1), random.randrange(test.height + 1))
        test.setcolor(random.randrange(len(test.COLOR)))
        test.write(random.choice(sorted("abcdefghijklmnopqrstuvwxyz")))
    test.gotoxy(0, 0)


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

