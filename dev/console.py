""" CONSOLE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import os, sys, time#, random


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
                    cls()                       : Clears the console screen.
                    clreol()                    : Clears the content of the line right of the caret.
                    home()                      : Moves the caret to the beginning of the line.
                    gotoxy(x, y)                : Moves the caret to position (x, y)
                    write(*arg)                 : Writes the arguments to the console.
                    writeln(*arg)               : Like write(), but scrolls the caret to a new line.
            
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
    """ An expansion on the basic console class. Includes color ansi escape sequences. These can be incorporated in the
        text sent to write() and writeln().
        
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
                    demo()                      : To Do...
                    cls()                       : Clears the console screen.
                    clreol()                    : Clears the content of the line right of the caret.
                    home()                      : Moves the caret to the beginning of the line.
                    gotoxy(x, y)                : Moves the caret to position (x, y)
                    write(*arg)                 : Writes the arguments to the console. Any embedded color codes
                                                  are processed and the appropriate ANSI codes substitued.
                    writeln(*arg)               : Like write(), but scrolls the caret to a new line.
        
            USAGE:
                The syntax of an in-text escape sequence is as follows:
                    [c:([clr]|(fg|bg):(sys|rgb|gray):code)]
            
                A full colour picker can be printed to the console by using the demo() method.
            
            EXAMPLES:
                If you wanted to write "Hello world!" where the word "world" was displayed in a
                system yellow on a blue background, you would write it as follows: 
                    > Color.writeln("[c:bg:rgb:001]Hello [c:fg:sys:4]world[c:clr][c:bg:rgb:001]![c:clr]")
                
                Or if you were to write out an escape code, you would write it as:
                    > Color.writeln("To print a word in a system yellow foreground color use [c:]fg:sys:4]")
                
            RESEARCH:
                - https://docs.python.org/2/library/os.html#os.isatty
                - https://docs.python.org/2/library/sys.html#sys.platform
                - https://en.wikipedia.org/wiki/ANSI_escape_code
                - https://rosettacode.org/wiki/Terminal_control/Cursor_positioning#Python
    """
    #-- Constants -----------------------------------------------------------------------------------------------------
    (   BLACK,
        RED,
        GREEN,
        YELLOW,
        BLUE,
        MAGENTA,
        CYAN,
        LIGHT_GRAY,
        DARK_GRAY,
        LIGHT_RED,
        LIGHT_GREEN,
        LIGHT_YELLOW,
        LIGHT_BLUE,
        LIGHT_MAGENTA,
        LIGHT_CYAN,
        WHITE           ) = range(16)
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _stdout = None
    _stderr = None
    _stdtty = False
        
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        """ Initialises the class. """
        #-- [Inherited]
        Basic.__init__(self, stdout, stderr)
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @staticmethod
    @property
    def is_linux():
        """ Returns True if python is running on Linux. """
        #-- [Inherited]
        return Basic.is_linux
    
    
    @staticmethod
    @property
    def is_windows():
        """ Returns True if python is running on Windows. """
        #-- [Inherited]
        return Basic.is_windows
    
    
    @property
    def ansi_support(self):
        """ Returns True if primary output is a TTY and os is not windows. """
        #-- [Inherited]
        return Basic.ansi_support(self)
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    @staticmethod
    def _choke(number, vmax, vmin = 0):
        """ Restrains an integer within the vmin and vmax parameters (inclusive).
        """
        return max(vmin, min(vmax, int(number)))
    
    
    def _esc_color(self, is_fg, code):
        """ Returns an escape colour sequence if ANSI is supported. Otherwise it returns an empty string.
        """
        code = ""
        if self.ansi_support:
            code = "\x1b[{0:d};5;{1:d}m".format(38 if is_fg else 48, code)
        return code
    

    def _esc_rgb(self, is_fg, red, green, blue):
        """ Calculates and returns the RGB colour escape string if ANSI is supported in the console window. RGB values
            can be 0 to 6.
        """
        code = 16 + (((self._choke(red, 6) * 6) + self._choke(green, 6)) * 6) + self._choke(blue, 6)
        return self._esc_color(is_fg, code)
    
    
    def _esc_sys(self, is_fg, color_code):
        """ Calculates and returns the system colour escape string if ANSI is supported in the console window. See also
            the system constants.
        """
        return self._esc_color(is_fg, self._choke(color_code, 15))
    
    
    def _esc_gray(self, is_fg, color_code):
        """ Calculates and returns the grayscale colour escape string if ANSI is supported in the console window.
            Grayscale values can be 0 to 23.
        """
        return self._esc_color(is_fg, 232 + self._choke(color_code, 23))
    
    
    def _esc_reset(self):
        """ Returns an reset escape sequence if ANSI is supported. Otherwise it returns just an empty string.
        """
        code = ""
        if self.ansi_support:
            code = "\x1b[0m"
        return code
    

    def _parse_colours(self, arg_list):
        """ Taste the rainbow! :D
            [c:([clr]|(fg|bg):(sys|rgb|gray):code)]
        """
        new_args = []
        for arg in arg_list:
            if type(arg) is str:
                if arg.count("[c:") == 0:
                    #-- No tokens found
                    new_args.append(arg)
                else:
                    #-- Parse tokens
                    splode = arg.split("[c:")
                    temp = splode[0]
                    for sploded in splode[1:]:
                        flag = len(temp)
                        if sploded.count("]") > 0:
                            s_end = sploded[sploded.index("]") + 1:]
                            if sploded.startswith("]"):
                                #-- Add the "[c:" token escape code.
                                temp += "[c:" + s_end
                            elif sploded.startswith("clr]"):
                                #-- Add reset escape sequence
                                temp += self._esc_reset() + s_end
                            elif (sploded.count(":", 0, sploded.index("]")) == 2) and (sploded[0:4] in ["fg:", "bg:"]):
                                #-- Add colour escape sequence
                                is_fg = sploded.startswith("fg:")
                                c_code = sploded[sploded.index(":", 4) + 1:sploded.index("]")]
                                c_opt = sploded[3:sploded.index(":", 4)]
                                if (len(c_code) > 0) and (c_opt in ["sys", "gray", "rgb"]):
                                    if c_opt == "sys":
                                        #-- System colour
                                        temp += self._esc_sys(is_fg, c_code) + s_end
                                    elif (c_opt == "rgb") and (len(c_code) == 3):
                                        #-- RGB colour
                                        temp += self._esc_rgb(is_fg, c_code[0], c_code[1], c_code[2]) + s_end
                                    else:
                                        #-- Grayscale colour
                                        temp += self._esc_gray(is_fg, c_code) + s_end
                        
                        if flag == len(temp):
                            #-- Token was invalid and will be ignored. 
                            temp += "[c:" + sploded
                    new_args.append(temp)
            else:
                #-- Ignore
                new_args.append(arg)
        return new_args
    
    
    def _write(self, arg_list, linefeed):
        """ Tries to write to primary output. If an error occurs, it writes the error to the secondary output. The main
            difference between this and the inherited _write() method is the parsing of colour escape sequences.
        """
        #-- [Inherited]
        Basic._write(self, self._parse_colours(arg_list), linefeed)
    
    
    def _error(self, message):
        """ Tries to write to secondary output. If _stderr is None, no output gets written. If an error occurs and 
            _stderr is not None, a fatal exception is raised and the program terminates.
        """
        #-- [Inherited]
        Basic._error(self, message)
    
    
    def _ansi(self, code, *args):
        """ Returns the ansi escape sequence if the console supports it, or raises an error and returns an empty string
            if it doesn't.
        """
        #-- [Inherited]
        return Basic._ansi(self, code, *args)
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def cls(self):
        """ Clears the screen and resets the cursor to position (0; 0).
        """
        #-- [Inherited]
        Basic.cls(self)
    
    
    def clreol(self):
        """ Attempts to write the clreol ansi escape sequence to the console.
        """
        #-- [Inherited]
        Basic.clreol(self)
    
    
    def home(self):
        """ Writes the carriage return string literal to the primary output if it is a tty or raises an error and does
            nothing if it doesn't.
        """
        #-- [Inherited]
        Basic.home(self)
    
    
    def gotoxy(self, x, y):
        """ Moves the carriage to position (x; y).
        """
        #-- [Inherited]
        Basic.gotoxy(self, x, y)
    
    
    def write(self, *args):
        """ Writes to the primary output.
        """
        #-- [Inherited]
        Basic.write(self, *args)
    
    
    def writeln(self, *args):
        """ Like writeln, but adds an line-feed character to the end.
        """
        #-- [Inherited]
        Basic.writeln(self, *args)



#===================================================================================================[ CONSOLE CLASS ]==
class ConsoleX(object):
    """ Class to extend and simplify common console output like colour and font settings or dimension retrieval.
            EXPOSES:
                Constants:
                    COLOR
                    STYLE
                
                Properties:
                    (ro) [int] width            : Returns the console window width.
                    (ro) [int] height           : Returns the console window height.
                    (ro) [int] color            : Returns the current color.
                    (ro) [int] backgroundcolor  : Returns the current background color.
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
def show_picker():
    """ Let's loopify this thing. """
    def write_color(x, y, fgc, bgc, text):
        """ Writes in color to stdout at position (x, y) and resets the format afterward.
        """
        sys.stdout.write("\x1b[{1};{0}H".format(x + 1, y + 1))  #-- GotoXY
        sys.stdout.write("\x1b[38;5;{0:d}m".format(fgc))        #-- Set FG
        sys.stdout.write("\x1b[48;5;{0:d}m".format(bgc))        #-- Set BG
        sys.stdout.write("{0}\x1b[0m".format(text))             #-- Write Text to screen
        sys.stdout.flush()
        
    def block(x, y, bgc, label="", fgc=15):
        """ Draws a block at position (x, y) on screen.
        """
        write_color(x, y,     fgc, bgc, (label + "    ")[0:4])
        write_color(x, y + 1, fgc, bgc, "    ")
    
    #-- Cls
    sys.stdout.write("\x1b[2J\x1b[0;0H")
    sys.stdout.flush()
    
    #-- RGB Hexagon (Based on http://coolmaxhot.com/graphics/hex-colorsA.gif)
    for x in range(11):
        inv_x = 10 - x
        offset = abs(5 - x)
        length = 11 - offset
        for y in range(length):
            inv_y = length - (y + 1)
            
            #-- Light
            red = min(5, inv_y)
            grn = min(5, x) + min(0, 5 - inv_y)
            blu = min(5, inv_x) + min(0, 5 - inv_y)
            block(x * 4, offset + y * 2, 16 + (red * 36) + (grn * 6) + blu, "{0}{1}{2}".format(red, grn, blu), 0)
            
            #-- Dark
            red = 5 - (min(5, y))
            grn = 5 - (min(5, x) + min(0, 5 - y))
            blu = 5 - (min(5, inv_x) + min(0, 5 - y))
            block((10 + x) * 4, offset + y * 2, 16 + (red * 36) + (grn * 6) + blu, "{0}{1}{2}".format(red, grn, blu))
    
    #-- RGB Grayscale
    for i in range(1, 5):
        block(2 + (7 + i) * 4,  0, 16 + (i * 36) + (i * 6) + i, "{0}{1}{2}".format(i, i, i))
    
    #-- Grayscale Bar
    for i in range(24):
        x = (i % 12) * 4
        y = 23 + (0 if i < 12 else 2)
        block(x, y, 232 + i, "G{0:02d}".format(i), (15 if i < 12 else 0))
    
    #-- System Color Bar
    for i in range(16):
        x = (13 + (i % 8)) * 4
        y = 23 + (0 if i < 8 else 2)
        block(x, y, i, "S{0:02d}".format(i), (15 if i < 8 else 0))
    
    #-- Position cursor
    sys.stdout.write("\x1b[29;0H")


def debug():
    """ Test method. """
    show_picker()
    
    #sploded = "fg:sys:24]abc"
    #is_fg = sploded.startswith("fg:")
    #code = sploded[sploded.index(":", 4) + 1:sploded.index("]")]
    #opt = sploded[3:sploded.index(":", 4)]
    #print is_fg, opt, code
    
    #-- Pipe type test
    #print "system:", sys.platform
    #with open('setup.txt', "w+") as fobj:
    #    print "file:  ", type(fobj).__name__, os.isatty(fobj.fileno())
    #print "stdout:", type(sys.stdout).__name__, os.isatty(sys.stdout.fileno())
    #print "stderr:", type(sys.stderr).__name__, os.isatty(sys.stderr.fileno())
    #print
    
    #-- Magic stars test
    #def print_test(*args):
    #    """ Troll or not a troll... """
    #    print args
    #test_tuple = (1,2,3,4,5,6)
    #print_test(test_tuple)
    #print_test(*test_tuple)
    
    #-- ConsoleX test
    #test = ConsoleX()
    #test.cls()
    #for _ in xrange(500):
    #    test.gotoxy(random.randrange(test.width + 1), random.randrange(test.height + 1))
    #    test.setcolor(random.randrange(len(test.COLOR)))
    #    test.write(random.choice(sorted("abcdefghijklmnopqrstuvwxyz")))
    #test.gotoxy(0, 0)


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

