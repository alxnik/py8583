import py8583
from py8583 import Iso8583, MemDump, DT, LT
from py8583spec import IsoSpec1987BCD, IsoSpec1987ASCII
import binascii
import unittest

class AsciiParse(unittest.TestCase):
    
    def setUp(self):
        self.IsoPacket = Iso8583(IsoSpec = IsoSpec1987ASCII())
        self.IsoPacket.Strict(True)
    
    def tearDown(self):
        pass
    
    def test_MTI(self):
        # positive test
        for b1 in range(0, 9):
            for b2 in range(1, 9):
                for b3 in range(0,9):
                    for b4 in range(0, 5):
                        MTI = str(b1) + str(b2) + str(b3) + str(b4)
                        self.IsoPacket.SetIsoContent(MTI + "0000000000000000")
                        self.assertEqual(self.IsoPacket.MTI(), MTI)
    
        # negative test
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket.SetIsoContent("000A")
            
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket.SetIsoContent("0000")
            
        for b4 in range(6, 9):
            with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
                MTI = "010" + str(b4)
                self.IsoPacket.SetIsoContent(MTI)
                
    def test_Bitmap(self):
        pass
                
class BCDParse(unittest.TestCase):
    
    def setUp(self):
        self.IsoPacket = Iso8583(IsoSpec = IsoSpec1987BCD())
        self.IsoPacket.Strict(True)
    
    def tearDown(self):
        pass
    
    def test_MTI(self):
        # positive test
        for b1 in range(0, 9):
            for b2 in range(1, 9):
                for b3 in range(0,9):
                    for b4 in range(0, 5):                        
                        MTI = str(b1) + str(b2) + str(b3) + str(b4)
                        self.IsoPacket.SetIsoContent(binascii.unhexlify(MTI + "0000000000000000"))
                        self.assertEqual(self.IsoPacket.MTI(), MTI)
                        
        # negative test
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket.SetIsoContent(binascii.unhexlify("000A"))

        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket.SetIsoContent(binascii.unhexlify("0000"))
            
        for b4 in range(6, 9):
            with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
                MTI = binascii.unhexlify("010" + str(b4))
                self.IsoPacket.SetIsoContent(MTI)
    
    def test_Bitmap(self):
        pass
                
    
    