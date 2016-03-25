#py8583
###Python library implementing the ISO-8583 banking protocol

This is an implementation of the de-facto protocol for banking applications, iso8583.

#### Status:
**Things working:**

* iso-8583/1987 parsing and building
* Support of BCD/Binary/ASCII variations in field lengths and field data (where applicable)
* Python 2.7 and 3.x support

**Things that will work** (aka TODO List):

* Proper documentation
* Fully automated unit testing
* 1993 and 2003 specifications of the protocol

**Things that might work** (aka Wishlist):

* Predefined (and ready to use) popular implementations
* EBCDIC support

#### How to use:
The module's external module dependencies are:

* enum34 (for python &lt; 3.4)
    
This paragraph will eventually have some basic/quick examples too. Until then, please have a look at the IsoHost.py file which contains a simple server which waits for ISO messages, parses them and replies in a hardcoded manner.

#### License:
All the work is licensed under LGPL 2.1. Since LGPL is not very python focused, as the copyright holder, my intentions 
basically boil down to:

* You are allowed to use the library as an API in closed source code without it being considered derivative work
* You are NOT allowed to modify the library itself without publishing the changes in a compatible license
