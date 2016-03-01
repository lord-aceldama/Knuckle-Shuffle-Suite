""" ROUTER
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import version, re


#====================================================================================================[ ROUTER CLASS ]==
class Router(object):
    """ A class designed to get the default router keyspaces and password lengths.
        
            RESEARCH:
                - https://forum.hashkiller.co.uk/topic-view.aspx?t=2715&p=0
                - https://docs.python.org/2/library/re.html
            
            EXPOSES:
                Constants:
                    VERSION
                
                Methods:
                    name                    : ?
                
                Functions:
                    [type] name             : ?
                
                Properties:
                    (rw) [str] name         : ?
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    VERSION  = version.Version("Router Defaults", 0, 9, 0)
    
    #--         Regex                        S   Charspace          Exploit Function
    _DB = {r"^SpeedTouch[.]*$"        : [10, "0-9a-f",          None],
           r"^BTHomeHub-[.]*$"        : [10, "0-9a-f",          None],
           r"^BTHomeHub2-[.]*$"       : [10, "2-9a-f",          None],
           r"^BTHub3-[.]*$"           : [10, "2-9a-f",          None],
           r"^BTHub4-[.]*$"           : [10, "2-9a-f",          None],
           r"^Thomson[.]*$"           : [10, "0-9a-f",          None],
           r"^PlusnetWireless[.]*$"   : [10, "0-9A-F",          None],
           r"^belkin.[.]{3, 4}$"      : [ 8, "2-9a-f",          None],
           r"^Belkin.[.]*$"           : [ 8, "0-9A-F",          None],
           r"^Belkin_[.]*$"           : [ 8, "0-9A-F",          None],
           r"^TP-LINK_[.]*$"          : [ 8, "0-9A-F",          None],
           r"^TDC-[.]*$"              : [ 9, "0-9A-F",          None],
           r"^TNCAP[.]*$"             : [10, "0-9A-F",          None],
           r"^TRKASHI-[.]*$"          : [10, "0-9",             None], #TRKASHI-###### - ?d?d###### [Broken]
           r"^WLAN1-[.]*$"            : [11, "0-9A-F",          None],
           r"^Telstra[.]*$"           : [10, "0-9A-F",          None],
           r"^BigPond[.]*$"           : [10, "0-9A-F",          None],
           r"^2WIRE[.]*$"             : [10, "0-9",             None],
           r"^ONO[.]*$"               : [10, "0-9",             None],
           r"^DJAWEB_[.]*$"           : [10, "0-9",             None],
           r"^TIM_PN51T[.]*$"         : [ 8, "0-9",             None], #WPS pin: 12345670. Can't be disabled
           r"^INFINITUM[.]*$"         : [10, "0-9",             None],
           r"^CenturyLink[.]*$"       : [14, "0-9a-f",          None],
           r"^BrightBox-[.]*$"        : [ 8, "0-9a-zA-Z",       None],
           r"^Orange-[.]*$"           : [ 8, "2-9ACEF",         None],
           r"^TALKTALK-[.]*$"         : [10, "A-'ILOS'Y3-'5'9", None],
           r"^AOLBB-[.]*$"            : [ 8, "0-9A-Z",          None],
           r"^UPC[.]*$"               : [ 8, "A-Z",             None],
           r"^SKY[.]*$"               : [ 8, "A-Z",             None], #http://www.ph-mb.com/products/sky-calc
           r"^Keenetic-[.]*$"         : [ 8, "0-9a-zA-Z",       None],
           r"^VM[\d]*-(2|5)G$"        : [ 8, "a-'io'z",         None],
           r"^FRITZ!Box Fon WLAN[.]*" : [16, "0-9",             None],
           r"^EasyBox-[.]*$"          : [ 9, "0-9A-F",          None],
           r"^MobileWifi-[.]*$"       : [ 8, "0-9",             None],
           r"^3Wireless-Modem-[.]*$"  : [ 8, "0-9A-F",          None], #4 ESSID digits are first 4 digits of key
           r"^UNITE-[.]*$"            : [ 8, "0-9",             None],
           r"^Verizon MIFI[.]*$"      : [11, "0-9",             None],
           r"^VirginMobile MiFi[.]*$" : [11, "0-9",             None],
           r"^E583[.]-[.]{4}$"        : [ 8, "0-9",             None],
           r"^E583[.]-[.]{5}$"        : [ 8, "0-9A-F",          None],
           r"^Domino-[.]*$"           : [ 8, "0-9A-F",          None]}

    #   NETGEARXX - Adjective + Noun + 3 Digits
    #      - KEY: vastcoconut260
    #   Livebox-XXXX - Think this one is long so nearly impossible unless default algorithm is found.
    #   EEBrightBox-XXXXXX - [3 word with hyphens]
    #      - See http://forum.md5decrypter.co.uk/topic1660-brightbox.aspx thread for details.
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _essid      = ""
    _bssid      = ""
    _keylen     = -1
    _charspace  = ""
    _exploit    = None
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, essid, bssid="00:00:00:00:00:00"):
        """ Initializes the object.
        """
        self.essid = essid
        idx = 0
        while idx < len(self._DB.keys):
            re.match(self._DB.keys[idx], essid + bssid)
            idx += 1
    
    
    def __str__(self):
        """ Returns a string representation of the version.
        """
        result = ""
        return result
        
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def in_db(self):
        """ Returns the name. """
        return self._keylen > 0
    
    
    @property
    def key_length(self):
        """ Returns the name. """
        return self._keylen
    
    
    @property
    def key_chars(self):
        """ Returns the name. """
        return self._charspace
    
    
    @property
    def exploit(self):
        """ Returns the name. """
        return self._exploit
    
    
    @property
    def bssid(self):
        """ Returns the router bssid.. """
        return self._bssid
    @bssid.setter
    def bssid(self, value):
        """ Sets the router bssid. """
        self._bssid = value
    
    
    @property
    def essid(self):
        """ Returns the router essid.. """
        return self._essid
    @essid.setter
    def essid(self, value):
        """ Sets the router essid. """
        self._essid = value
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #[None]


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
 

#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

