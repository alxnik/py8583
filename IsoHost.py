import socket
import sys
import traceback
import struct
import os

from py8583 import Iso8583, MemDump, DT, LT, Str2Bcd, Int2Bcd

class TestIso(Iso8583):
    def Config(self):
        self.SetDataType('MTI', DT.BCD)
        self.SetDataType('Bitmap', DT.BIN)
        
            
        for i in range(0,128):
            if i in self.DataTypes.keys():
                if self.GetContentType(i) == 'n' or self.GetContentType(i) == 'z':
                    self.SetDataType(i, DT.BCD)
                    
                    if('LenDataType' in self.DataTypes[i]):
                        self.DataTypes[i]['LenDataType'] = DT.BCD
    
                elif self.GetContentType(i) == 'b':
                    self.SetDataType(i, DT.BIN)
                
        self.DataTypes[60]['LenDataType'] = DT.BCD
        self.SetContentType(60, 'b')
        self.SetDataType(60, DT.BIN)
        
        self.DataTypes[48]['LenDataType'] = DT.BCD
        self.SetContentType(48, 'b')
        self.SetDataType(48, DT.BIN)
        
        self.DataTypes[63]['LenDataType'] = DT.BCD
        self.SetContentType(63, 'b')
        self.SetDataType(63, DT.BIN)
        
        self.DataTypes[55]['LenDataType'] = DT.BCD
        self.SetContentType(55, 'b')
        self.SetDataType(55, DT.BIN)



HOST = ''
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
    

s.listen(10)


while True:
    try:
        print ('Waiting for connections')
        conn, addr = s.accept()
        print ('Connected: ' + addr[0] + ':' + str(addr[1]))
        data = conn.recv(4096)
        MemDump("Received:", data)
        
        Len = struct.unpack_from("!H", data[:2])[0]
        
        if(Len != len(data) - 2):
            print "Invalid length {0} - {1}".format(Len, len(data) - 2)
            conn.close()
            continue
        
        IsoPacket = TestIso(data[2:])
        IsoPacket.PrintMessage()
        
        IsoPacket.MTI = "0210"
        
        IsoPacket.SetField(39)
        IsoPacket.FieldData[39] = "00"
        IsoPacket.ResetField(2)
        IsoPacket.ResetField(35)
        IsoPacket.ResetField(52)
        IsoPacket.ResetField(60)
         
        data = IsoPacket.BuildIso()
        data = Str2Bcd("{0:04d}".format(len(data))) + data
        MemDump("Sending:", data)
        conn.send(data)
        
    except Exception, ex:
        print ex
#         print(traceback.format_exc())
    conn.close()
    
s.close()
sys.exit()