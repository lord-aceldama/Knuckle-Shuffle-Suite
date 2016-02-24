""" CONSOLE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import os, sys, time, random


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
                    setbackgroundcolor()        : Sets the background color.
                    check_size()                : Forces a re-check of the window width and height.
                    write(text)                 : Writes the text to the console.
                    writeln(text)               : Same as write() with a newline.
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
    def reset(self):
        """ Resets colours and styles to their default values without clearing the console. """
        self.setcolor(self._DEFAULTS[0])
        self.setbackgroundcolor(self._DEFAULTS[1])
        self.bright = self._DEFAULTS[2]
        self.underline = self._DEFAULTS[3]
        self.write("")
    
    
    @staticmethod
    def cls():
        """ Clears the console but does not alter colors and styles. """
        os.system('cls' if os.name=='nt' else 'clear')
    
    
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
    test = Console()
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

