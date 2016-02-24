""" CONSOLE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import os, sys


#===================================================================================================[ CONSOLE CLASS ]==
class Console(object):
    """ Class to extend and simplify common console output like colour and font settings or dimension retrieval.
            RESEARCH:
                - https://en.wikipedia.org/wiki/ANSI_escape_code
                - http://ozzmaker.com/add-colour-to-text-in-python/
                - https://rosettacode.org/wiki/Terminal_control/Cursor_positioning#Python
            
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
                    reset()                     : Resets color and style to the default without clearing screen.
                    cls()                       : Clears the screen.
                    gotoxy(pos_x, pos_y)        : Moves the cursor to position XY.
                    setcolor()                  : Sets the foreground color.
                    setbackgroundcolor()        : sets the background color.
                    write(text)                 : Writes the text to the console.
                    writeln(text)               : Same as write() with a newline.
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    _DEFAULTS = [7, 0, True, False]
    
    COLOR = [ "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white" ]
    STYLE = [ "none", "bright", "underline" ]
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _output = sys.stdout
    _color  = { "f" : 0, "b" : 0 }
    _style  = { "b" : False, "u" : False }
    _update = { "s" : False, "c" : False }
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, output = sys.stdout):
        """ Initializes the object.
        """
        self._output = output
        self.reset()
    
    
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
        return self._win_wh[0]
    
    
    @property
    def height(self):
        """ Returns the console height. """
        return self._win_wh[1]
    
    
    @property
    def color(self):
        """ Returns the current text color. """
        return self.COLOR[self._color["f"] - 30]
    
    
    @property
    def backgroundcolor(self):
        """ Returns the current text background color. """
        return self._color["b"] - 40
    
    
    @property
    def bright(self):
        """ Returns the current text background color. """
        return self._style["b"]
    @bright.setter
    def bright(self, value):
        """ X """
        if (type(value) == bool) and (self._style["b"] != value):
            self._update["s"] = True
            self._style["b"] = value
    
    
    @property
    def underline(self):
        """ Returns the current text background color. """
        return self._style["u"]
    @underline.setter
    def underline(self, value):
        """ X """
        if (type(value) == bool) and (self._style["u"] != value):
            self._update["s"] = True
            self._style["u"] = value
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    @staticmethod
    def _win_wh():
        """ X """
        return [int(x) for x in os.popen('stty size', 'r').read().split()]
    
    
    def _getcolor(self, color):
        """ X """
        result = None
        if (type(color) == int) and (color >= 0) and (color < 8):
            result = color
        elif type(color) == str:
            cleaned = color.strip().lower()
            if cleaned in self.COLOR:
                result = self.COLOR.index(cleaned)
        assert (result is not None), "Bad color"
        return result
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def reset(self):
        """ X """
        self.setcolor(self._DEFAULTS[0])
        self.setbackgroundcolor(self._DEFAULTS[1])
        self.bright = self._DEFAULTS[2]
        self.underline = self._DEFAULTS[3]
        self.write("")
    
    
    def cls(self):
        """ X """
        os.system('cls' if os.name=='nt' else 'clear')
        self.write("")
    
    
    def gotoxy(self, pos_x, pos_y):
        """ X
        """
        self.write("\033[{1};{0}H".format(max(0, min(self.width - 1, int(pos_x))), 
                                          max(0, min(self.height - 1, int(pos_y)))))
    
    
    def setcolor(self, color):
        """ X """
        col = self._getcolor(color)
        if self._color["f"] != 30 + col:
            self._update["c"] = True
            self._color["f"] = 30 + col
            
    
    
    def setbackgroundcolor(self, color):
        """ X """
        col = self._getcolor(color)
        if self._color["b"] != 40 + col:
            self._update["c"] = True
            self._color["b"] = 40 + col
    
    
    def write(self, text):
        """ X """
        prefix = ""
        if self._update["c"] or self._update["s"]:
            self._update["c"] = False
            self._update["s"] = False
            prefix += "\033[0;{0};{1}m".format(self._color["f"], self._color["b"])
            if self.bright:
                prefix += "\033[1;{0};{1}m".format(self._color["f"], self._color["b"])
            if self.underline:
                prefix += "\033[4;{0};{1}m".format(self._color["f"], self._color["b"])
        self._output.write(prefix + text)
        
    
    def writeln(self, text):
        """ X """
        self.write("{0}\n".format(text))


#============================================================================================================[ MAIN ]==
#[None]
test = Console()
print test
test.write("xxx")
test.underline = True
test.write("xxx")
test.underline = False
test.writeln("xxx")

