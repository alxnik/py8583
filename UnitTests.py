import py8583
from py8583 import Iso8583, MemDump
from py8583spec import DT, LT
import binascii
import unittest


class MTIParse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    def test_SpecErrors(self):
        self.IsoPacket = Iso8583()
        with self.assertRaisesRegexp(py8583.SpecError, "Cannot set DataType"):
            self.IsoPacket.SetDataType('MTI', DT.BIN)
        
    def test_Ascii_Positive(self):
        for b1 in range(0, 9):
            for b2 in range(1, 9):
                for b3 in range(0,9):
                    for b4 in range(0, 5):
                        MTI = str(b1) + str(b2) + str(b3) + str(b4)
                        IsoContent = MTI + "0000000000000000"
                        self.IsoPacket = Iso8583(IsoContent)
                        self.assertEqual(self.IsoPacket.GetMTI(), MTI)

    def test_Ascii_Negative(self):
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket = Iso8583()
            self.IsoPacket.Strict(True)
            self.IsoPacket.SetIsoContent("000A")
            
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket = Iso8583()
            self.IsoPacket.Strict(True)
            self.IsoPacket.SetIsoContent("0000")
            
        for b4 in range(6, 9):
            MTI = "010" + str(b4)
            with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
                self.IsoPacket = Iso8583()
                self.IsoPacket.Strict(True)
                self.IsoPacket.SetIsoContent(MTI)

    def test_BCD_Positive(self):
        for b1 in range(0, 9):
            for b2 in range(1, 9):
                for b3 in range(0,9):
                    for b4 in range(0, 5):
                        self.IsoPacket = Iso8583()
                        self.IsoPacket.SetDataType('MTI', DT.BCD)
                        self.IsoPacket.SetDataType('Bitmap', DT.BIN)
                        MTI = str(b1) + str(b2) + str(b3) + str(b4)
                        IsoContent = binascii.unhexlify(MTI + "0000000000000000")
                        self.IsoPacket.SetIsoContent(IsoContent)
                        self.assertEqual(self.IsoPacket.GetMTI(), MTI)
                        
    def test_BCD_Negative(self):
        self.IsoPacket = Iso8583()
        
        self.IsoPacket.SetDataType('MTI', DT.BCD)
        self.IsoPacket.SetDataType('Bitmap', DT.BIN)
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket.SetIsoContent(binascii.unhexlify("000A"))
        
        self.IsoPacket = Iso8583()
        self.IsoPacket.Strict(True)
        self.IsoPacket.SetDataType('MTI', DT.BCD)
        self.IsoPacket.SetDataType('Bitmap', DT.BIN)
        with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
            self.IsoPacket.SetIsoContent(binascii.unhexlify("0000"))
            
        for b4 in range(6, 9):
            self.IsoPacket = Iso8583()
            self.IsoPacket.Strict(True)
            self.IsoPacket.SetDataType('MTI', DT.BCD)
            self.IsoPacket.SetDataType('Bitmap', DT.BIN)
            MTI = binascii.unhexlify("010" + str(b4))
            with self.assertRaisesRegexp(py8583.ParseError, "Invalid MTI"):
                self.IsoPacket.SetIsoContent(MTI)
                
                
class BitmapParse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_SpecErrors(self):
        self.IsoPacket = Iso8583()
        with self.assertRaisesRegexp(py8583.SpecError, "Cannot set DataType"):
            self.IsoPacket.SetDataType('Bitmap', DT.BCD)
    
    
    
    