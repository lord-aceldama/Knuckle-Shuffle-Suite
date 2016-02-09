""" XIFO (FIFO and LIFO)
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
#[None]


#=====================================================================================================[ QUEUE CLASS ]==
class Queue(object):
    """ Simple Queue class. They don't get much simpler than this...
    """
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _items = []
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self):
        """ Initializes the object.
        """
        self._items = []
    
    
    def __str__(self):
        """ Returns a string representation of the queue.
        """
        string = 'Q[%s](' % len(self)               # Q[0](
        if len(self) > 0:
            if len(self) > 1:
                string += '%s, ' % self._items[0]   # Q[0]([X, ]
                if len(self) > 2:
                    string += '..., '               # Q[0]([X, [..., ]]
            string += '%s' % self._items[-1]        # Q[0]([X, [..., ]][N]
        return string + ")"                         # Q[0]([X, [..., ]][N])
    
    
    def __len__(self):
        """ Returns the length of the queue. """
        return len(self._items)
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def empty(self):
        """ Returns True if the queue is empty. """
        return len(self) == 0
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def push(self, value):
        """ Appends a value to the end of the list. """
        self._items.append(value)
    
    
    def pop(self):
        """ Removes and returns the last item in the queue. """
        value = None
        if len(self._items) > 0:
            value = self._items.pop(0)
        return value


#=====================================================================================================[ STACK CLASS ]==
class Stack(Queue):
    """ Simple array-stack class for use in the Shuffle class. 
            Using properties:  http://blaag.haard.se/What-s-the-point-of-properties-in-Python/
    """
    
    #-- Constants
    EXPAND_BY = 5
    
    
    #-- Global Vars
    _items = None
    _index = None
    
    
    #-- Special class methods -----------------------------------------------------------------------------------------
    def __init__(self):
        """ Initializes the object.
        """
        Queue.__init__(self)
        self._items = []
        self._index = -1
    
    
    def __str__(self):
        """ Returns a string representation of the stack.
        """
        return "S" + Queue.__str__(self)[1:]
    
    
    def __len__(self):
        """ Returns the number of items on the stack.
        """
        return self._index + 1
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def top(self):
        """ Returns the top value of the stack. Will return None if the stack is empty.
        """
        value = self.value_at(self._index)
        return value
    
    
    @property
    def empty(self):
        """ Returns True if there are no items on the stack, ie. len(self) == 0.
        """
        return len(self) == 0
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def push(self, value):
        """ Adds a key-value pair to the top of the stack and returns the new stack length.
        """
        #-- Inrease the stack index
        self._index += 1

        #-- Expand internal stack if necessary.
        if len(self._items) == self._index:
            idx = 0
            while idx < self.EXPAND_BY:
                self._items.append(None)
                idx += 1
        
        #-- Update the value.
        self._items[self._index] = value
        
        #-- Return the new stack length.
        return len(self)
    
    
    def pop(self):
        """ Pops the top value off the stack and returns it. Will return None if the stack is empty.
        """
        value = self.top
        self._index = max(-1, self._index - 1)
        return value
    
    
    def value_at(self, pos):
        """ Returns the value at a specific position on the stack. Will return None if the stack is empty.
        """
        value = None
        if (pos >= 0) and (pos <= self._index):
            value = self._items[pos]
        
        return value


#=====================================================================================================[ STACK CLASS ]==
class DictStack(Stack):
    """ Simple array-stack class for use in the Shuffle class. 
            Using properties:  http://blaag.haard.se/What-s-the-point-of-properties-in-Python/
    """
    
    #-- Constants
    EXPAND_BY = 5
    
    
    #-- Global Vars
    # Inherits: _stack, _index
    _structure = None
    
    
    #-- Special class methods -----------------------------------------------------------------------------------------
    def __init__(self, **default_dict):
        """ Initializes the object.
        """
        Stack.__init__(self)
        
        self._structure = dict()
        for key, value in default_dict.iteritems():
            self._structure[key] = value
    
    
    def __str__(self):
        """ Returns a string representation of the stack.
        """
        return Stack.__str__(self)
    
    
    def __len__(self):
        """ Returns the number of items on the stack.
        """
        return Stack.__len__(self)
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def top(self):
        """ Returns the top value of the stack. Will return None if the stack is empty.
        """
        return self.value_at(self._index)
    
    
    @property
    def empty(self):
        """ Returns True if there are no items on the stack, ie. len(self) == 0.
        """
        return len(self) == 0
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def push(self, **kv_pairs):
        """ Adds a key-value pair to the top of the stack and returns the new stack length.
        """
        #-- Inrease the stack index
        self._index += 1

        #-- Expand internal stack if necessary.
        if len(self._items) == self._index:
            idx = 0
            while idx < 5:
                self._items.append(self._structure.copy())
                idx += 1
        
        #-- Update the value.
        for key, value in kv_pairs.iteritems():
            self._items[self._index][key] = value
        
        #-- Return the new stack length.
        return len(self)
    
    
    def pop(self):
        """ Pops the top value off the stack and returns a copy of it. Will return None if the stack is empty.
        """
        return Stack.pop(self)
    
    
    def value_at(self, pos):
        """ Returns the value at a specific position on the stack. Will return None if the stack is empty.
        """
        return Stack.value_at(self, pos)


#====================================================================================================[ TEST METHODS ]==
def test_xifo():
    """ Test run """
    test = DictStack(key1=0, key2=0)
    print test

    test.push(key1=555)
    print test

    test.push(key1=666)
    print test

    test.push(key1=123)
    print test

    test.top["key2"] = 456
    print test

    print test.top, test
    print test.pop()


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    test_xifo()

