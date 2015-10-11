<h1>py8583</h1>
<h3>Python library implementing the ISO-8583 banking protocol</h3>

<br/>
<p>
This is an implementation of the de-facto protocol for banking applications, iso8583.
</p>
<br/>

<h4>Status:</h4>
<b>Things working:</b><br/>
<li>
    <ul>iso-8583/1987 parsing and building up to 64 fields</ul>
    <ul>Support of BCD/Binary/ASCII variations in field lengths and field data (where applicable)</ul>
    <ul>Python 2.7 support</ul>
</li>
<b>Things that will work</b> (aka TODO List):<br/>
<li>
    <ul>Proper documentation</ul>
    <ul>Python 3.x support</ul>
    <ul>Fully automated unit testing</ul>
    <ul>128 data fields (secondary bitmap)</ul>
    <ul>1993 and 2003 specifications of the protocol</ul>
</li>
<b>Things that might work</b> (aka Wishlist):<br/>
<li>
    <ul>Predefined (and ready to use) popular implementations</ul>
    <ul>EBCDIC support</ul>
</li>
<br/>
<h4>How to use:</h4>
The module's external module dependencies are:
<li>
    <ul>binascii</ul>
    <ul>struct</ul>
    <ul>enum34 (for python &lt; 3.4)</ul>
</li>
This paragraph will eventually have some basic/quick examples too. Until then, please have a look at the IsoHost.py file which contains a simple server which waits for ISO messages, parses them and replies in a hardcoded manner.

<br/>
<h4>License:</h4>
All the work is licensed under LGPL 2.1. Since LGPL is not very python focused, as the copyright holder, my intentions 
basically boil down to:<br/>
<li>
    <ul>You are allowed to use the library as an API in closed source code without it being considered derivative work</ul>
    <ul>You are NOT allowed to modify the library itself without publishing the changes in a compatible license</ul>
</li>
