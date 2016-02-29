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
    KEYSPACE = {"^SpeedTouch[.]*$"        : [10, "0-9a-f",          None],
                "^BTHomeHub-[.]*$"        : [10, "0-9a-f",          None],
                "^BTHomeHub2-[.]*$"       : [10, "2-9a-f",          None],
                "^BTHub3-[.]*$"           : [10, "2-9a-f",          None],
                "^BTHub4-[.]*$"           : [10, "2-9a-f",          None],
                "^Thomson[.]*$"           : [10, "0-9a-f",          None],
                "^PlusnetWireless[.]*$"   : [10, "0-9A-F",          None],
                "^belkin.[.]{3, 4}$"      : [ 8, "2-9a-f",          None],
                "^Belkin.[.]*$"           : [ 8, "0-9A-F",          None],
                "^Belkin_[.]*$"           : [ 8, "0-9A-F",          None],
                "^TP-LINK_[.]*$"          : [ 8, "0-9A-F",          None],
                "^TDC-[.]*$"              : [ 9, "0-9A-F",          None],
                "^TNCAP[.]*$"             : [10, "0-9A-F",          None],
                "^TDC-[.]*$"              : [10, "0-9A-F",          None],
                "^TRKASHI-[.]*$"          : [10, "0-9",             None], #TRKASHI-###### - ?d?d###### [Broken]
                "^WLAN1-[.]*$"            : [11, "0-9A-F",          None],
                "^Telstra[.]*"            : [10, "0-9A-F",          None],
                "^BigPond[.]*"            : [10, "0-9A-F",          None],
                "^2WIRE[.]*"              : [10, "0-9",             None],
                "^ONO[.]*"                : [10, "0-9",             None],
                "^DJAWEB_[.]*"            : [10, "0-9",             None],
                "^TIM_PN51T[.]*"          : [ 8, "0-9",             None], #WPS pin: 12345670. Can't be disabled
                "^INFINITUM[.]*"          : [10, "0-9",             None],
                "^CenturyLink[.]*"        : [14, "0-9a-f",          None],
                "^BrightBox-[.]*"         : [ 8, "0-9a-zA-Z",       None],
                "^Orange-[.]*"            : [ 8, "2-9ACEF",         None],
                "^TALKTALK-[.]*"          : [10, "A-'ILOS'Y3-'5'9", None],
                "^AOLBB-[.]*"             : [ 8, "0-9A-Z",          None],
                "^UPC[.]*"                : [ 8, "A-Z",             None],
                "^SKY[.]*"                : [ 8, "A-Z",             None],
                "^Keenetic-[.]*"          : [ 8, "0-9a-zA-Z",       None],
                "^VM[\d]*-(2|5)G$"        : [ 8, "a-'io'z",         None],
                "^FRITZ!Box Fon WLAN[.]*" : [16, "0-9",             None],
                "^EasyBox-[.]*"           : [ 9, "0-9A-F",          None],
                "^MobileWifi-[.]*"        : [ 8, "0-9",             None],
                "^3Wireless-Modem-[.]*"   : [ 8, "0-9A-F",          None], #4 ESSID digits are first 4 digits of key
                "^UNITE-[.]*"             : [ 8, "0-9"              None],
                "^Verizon MIFI[.]*"       : [11, "0-9",             None],
                "^VirginMobile MiFi[.]*"  : [11, "0-9",             None],
                "^E583[.]-[.]{4}"         : [ 8, "0-9",             None],
                "^E583[.]-[.]{5}*"        : [ 8, "0-9A-F",          None],
                "^Domino-[.]*"            : [ 8, "0-9A-F",          None]}

    #   NETGEARXX - Adjective + Noun + 3 Digits
    #      - KEY: vastcoconut260
    #   Livebox-XXXX - Think this one is long so nearly impossible unless default algorithm is found.
    #   EEBrightBox-XXXXXX - [3 word with hyphens]
    #      - See http://forum.md5decrypter.co.uk/topic1660-brightbox.aspx thread for details.
    #   SKYXXXXX - [A-Z] Len: 8
    #    - SKY keygen: http://www.ph-mb.com/products/sky-calc
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, essid, bssid="00:00:00:00:00:00"):
        """ Initializes the object.
        """
    
    
    def __str__(self):
        """ Returns a string representation of the version.
        """
        result = ""
        return result
        
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def name(self):
        """ Returns the name. """
        return self._name
    @name.setter
    def name(self, value):
        """ Sets the name. """
    
    
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

