import binascii
import struct
from enum import Enum

# Data Type enumeration
class DT(Enum):
    BCD     = 1
    ASCII   = 2
    BIN     = 3

# Length Type enumeration
class LT(Enum):
    FIXED   = 0
    LVAR    = 1
    LLVAR   = 2
    LLLVAR  = 3

def MemDump(Title, data):
    i = 1

    print(Title)
    for c in data:
        print("{:02x}".format(ord(c))),
        
        if(i % 16 == 0):
            print("")
        i+=1
    print("\n")

def Bcd2Str(bcd):
    return binascii.hexlify(bcd)

def Str2Bcd(string):
    if(len(string) % 2 == 1):
        string = string.zfill(len(string) + 1)
    return binascii.unhexlify(string)

def Bcd2Int(bcd):
    return int(Bcd2Str(bcd))

def Int2Bcd(integer):
    string = str(integer)
    if(len(string) % 2 == 1):
        string = string.zfill(len(string) + 1)

    return binascii.unhexlify(string)


class ParseError(Exception):
        def __init__(self, value):
                self.str = value
        def __str__(self):
                return repr(self.str)
class SpecError(Exception):
        def __init__(self, value):
                self.str = value
        def __str__(self):
                return repr(self.str)

import py8583spec    
class Iso8583:

    
    ValidContentTypes = ('a', 'n', 's', 'an', 'as', 'ns', 'ans', 'b', 'z')

    Strict = False
    
    DataTypes = '';
    
    HeaderDataTypes = {
        'MTI':    { 'DataType': DT.ASCII },
        'Bitmap': { 'DataType': DT.ASCII },
    }
    
    Bitmap = {}
    FieldData = {}
    
    def Strict(self, Value):
        if(Value != True and Value != False):
            raise ValueError
        self.Strict = Value
        
    def CheckTableConsistency(self):
        for field in self.DataTypes:
            
            if(self.DataTypes[field]['LenType'] != LT.FIXED and 'LenDataType' not in self.DataTypes[field].keys()):
                raise SpecError("{0} is variable length but length data type not defined".format(field))
            
            ContentType = self.DataTypes[field]['ContentType']
            DataType = self.DataTypes[field]['DataType']
            
            if(ContentType not in self.ValidContentTypes):
                raise SpecError("{0} has invalid content type [{1}]".format(field, ContentType))
            
            if(("a" in ContentType or "s" in ContentType) and DataType != DT.ASCII):
                raise SpecError("{0} is defined as {1} and must be defined as ASCII".format(field, ContentType))
            if(ContentType == "b" and DataType == DT.BCD):
                raise SpecError("{0} is defined as {1} and cannot be BCD".format(field, ContentType))
    
    
    
    
    def __init__(self,iso=""):
        self.SetSpec(py8583spec.Iso1987Ascii)
        self.CheckTableConsistency()
        self.iso = iso
        if(self.iso != ""):
            self.ParseIso()
            
    def SetSpec(self, spec):
        self.DataTypes = spec
        self.Config()
        
    def Config(self):
        pass
    
    
    
    
    
    def ParseMTI(self, p):
        if(self.HeaderDataTypes['MTI']['DataType'] == DT.BCD):
            self.MTI = Bcd2Str(self.iso[p:p+2])
            p+=2
        elif(self.HeaderDataTypes['MTI']['DataType'] == DT.ASCII):
            self.MTI = self.iso[p:p+4]
            p+=4
        
        try: # MTI should only contain numbers
            int(self.MTI)
        except:
            raise ParseError("Invalid MTI: [{0}]".format(self.MTI))
            
        if(self.Strict == True):
            if(self.MTI[1] == '0'):
                raise ParseError("Invalid MTI: Invalid Message type [{0}]".format(self.MTI))
                  
            if(int(self.MTI[3]) > 5):
                raise ParseError("Invalid MTI: Invalid Message origin [{0}]".format(self.MTI))
        
        return p
    
    
    def ParseBitmap(self, p):
        DataType = self.HeaderDataTypes['Bitmap']['DataType']

        if(DataType == DT.BIN):
            Primary = self.iso[p:p+8]
            p += 8
        elif(DataType == DT.ASCII):
            Primary = binascii.unhexlify(self.iso[p:p+16])
            p += 16
                
        IntPrimary = struct.unpack_from("!Q", Primary)[0]
        
        for i in range(1, 65):
            self.Bitmap[i] = (IntPrimary >> (64 - i)) & 0x1

        if(self.Bitmap[1] == 1):
            if(DataType == DT.BIN):
                Secondary = self.iso[p:p+8]
                p += 8
            elif(DataType == DT.ASCII):
                Secondary = binascii.unhexlify(self.iso[p:p+16])
                p += 16
                
            IntSecondary = struct.unpack_from("!Q", Secondary)[0]
            
            for i in range(1, 65):
                self.Bitmap[i+64] = (IntSecondary >> (64 - i)) & 0x1
            
        return p
            
    def ParseField(self, field, p):
         
        try:
            DataType = self.DataTypes[field]['DataType']
            LenType = self.DataTypes[field]['LenType']
            ContentType = self.DataTypes[field]['ContentType']
        except:
            raise SpecError("Cannot parse F{0}: Incomplete specification".format(field))
        

        try:
            if(LenType == LT.FIXED):
                Len = self.DataTypes[field]['MaxLen']
                if(DataType == DT.ASCII and ContentType == 'b'):
                    Len *= 2
            elif(LenType == LT.LVAR):
                pass
            elif(LenType == LT.LLVAR):
                LenDataType = self.DataTypes[field]['LenDataType']
                if(LenDataType == DT.ASCII):
                    Len = int(self.iso[p:p+2])
                    p+=2
                elif(LenDataType == DT.BCD):
                    Len = Bcd2Int(self.iso[p:p+1])
                    p+=1
            elif(LenType == LT.LLLVAR):
                LenDataType = self.DataTypes[field]['LenDataType']
                if(LenDataType == DT.ASCII):
                    Len = int(self.iso[p:p+3])
                    p+=3
                elif(LenDataType == DT.BCD):
                    Len = Bcd2Int(self.iso[p:p+2])
                    p+=2
        except ValueError:
            raise ParseError("Cannot parse F{0}: Invalid length".format(field))
            
        if(Len > self.DataTypes[field]['MaxLen']):
            raise ParseError("F{0} is larger than maximum length ({1}>{2})".format(field, Len, self.DataTypes[field]['MaxLen']))
        

        try:
            if(DataType == DT.ASCII):
                if(ContentType == 'n'):
                    self.FieldData[field] = int(self.iso[p:p+(Len)])
                else:
                    self.FieldData[field] = self.iso[p:p+(Len)]
                p += Len
            elif(DataType == DT.BCD):
                if(Len % 2 == 1):
                    Len += 1
                if(ContentType == 'n'):
                    self.FieldData[field] = Bcd2Int(self.iso[p:p+(Len/2)])
                elif(ContentType == 'z'):
                    self.FieldData[field] = binascii.hexlify(self.iso[p:p+(Len/2)]).upper()
                p += Len/2
            elif(DataType == DT.BIN):
                self.FieldData[field] = binascii.hexlify(self.iso[p:p+(Len)]).upper()
                p += Len
        except:
            raise ParseError("Cannot parse F{0}".format(field))
        
        if(ContentType == 'z'):
            self.FieldData[field] = self.FieldData[field].replace("D", "=") # in track2, replace d with =  
            self.FieldData[field] = self.FieldData[field].replace("F", "") # in track2, remove trailing f
 
        return p
    
    def ParseIso(self):
        self.CheckTableConsistency()
        
        p = 0
        p = self.ParseMTI(p)
        p = self.ParseBitmap(p)


        for field in self.Bitmap:
            if(self.IsSet(field) and field != 1):
                if(field not in self.DataTypes.keys()):
                    raise SpecError("Cannot parse F{0}: Unknown field spec".format(field))
                p = self.ParseField(field, p)
    
    
    



    def BuildMTI(self):
        
        try: # MTI should only contain numbers
            int(self.MTI)
        except:
            raise ParseError("Invalid MTI: [{0}]".format(self.MTI))
        
        if(self.Strict == True):
            if(self.MTI[1] == '0'):
                raise ParseError("Invalid MTI: Invalid Message type [{0}]".format(self.MTI))
                  
            if(int(self.MTI[3]) > 5):
                raise ParseError("Invalid MTI: Invalid Message origin [{0}]".format(self.MTI))
        
        
        if(self.HeaderDataTypes['MTI']['DataType'] == DT.BCD):
            self.iso += Str2Bcd(self.MTI)
        elif(self.HeaderDataTypes['MTI']['DataType'] == DT.ASCII):
            self.iso += self.MTI
    
    def BuildBitmap(self):
        DataType = self.HeaderDataTypes['Bitmap']['DataType']
        
        IntPrimary = 0
        for i in range(1, 65):
            IntPrimary |= (self.Bitmap[i] & 0x1) << (64 - i)

        Primary = struct.pack("!Q", IntPrimary)

        if(DataType == DT.BIN):
            self.iso += Primary
        elif(DataType == DT.ASCII):
            self.iso += binascii.hexlify(Primary)
            
            
    def BuildField(self, field):
        try:
            DataType = self.DataTypes[field]['DataType']
            LenType = self.DataTypes[field]['LenType']
            ContentType = self.DataTypes[field]['ContentType']
        except:
            raise SpecError("Cannot Build F{0}: Incomplete specification".format(field))
 

        data = ""
        if(LenType == LT.FIXED):
            Len = self.DataTypes[field]['MaxLen']
            
            if(ContentType == 'n'):
                formatter = "{{0:0{0}d}}".format(Len)
            elif('a' in ContentType or 'n' in ContentType or 's' in ContentType):
                formatter = "{{0: >{0}}}".format(Len)
            else:
                formatter = "{0}"
                
            data = formatter.format(self.FieldData[field])
#             print("{0}: [{1}]".format(field, data))
                
        else:
            LenDataType = self.DataTypes[field]['LenDataType']
            
            data = "{0}".format(self.FieldData[field])
            Len = len(data)
            if(DataType == DT.BIN):
                Len /=2
                
            if(LenType == LT.LVAR):
                if(Len > 9):
                    raise SpecError("Cannot Build F{0}: Field Length larger than specification".format(field))
                
                LenData = "{0:01d}".format(Len)
                
            elif(LenType == LT.LLVAR):
                if(Len > 99):
                    raise SpecError("Cannot Build F{0}: Field Length larger than specification".format(field))
                
                LenData = "{0:02d}".format(Len)
                
            elif(LenType == LT.LLLVAR):
                if(Len > 999):
                    raise SpecError("Cannot Build F{0}: Field Length larger than specification".format(field))
                
                LenData = "{0:03d}".format(Len)
                
            if(LenDataType == DT.ASCII):
                self.iso += LenData
            elif(LenDataType == DT.BCD):
                self.iso += Str2Bcd(LenData)
            elif(LenDataType == DT.BIN):
                self.iso += binascii.unhexlify(LenData)
            
            
        if(ContentType == 'z'):
            data = data.replace("=", "D")
            if(len(data) % 2 == 1):
                data = data + 'F'
        
        if(DataType == DT.ASCII):
            self.iso += data
        elif(DataType == DT.BCD):
            self.iso += Str2Bcd(data)
        elif(DataType == DT.BIN):
            self.iso += binascii.unhexlify(self.FieldData[field])


    def BuildIso(self):
        self.iso = ""
        self.BuildMTI()
        self.BuildBitmap()
        
        for field in self.Bitmap:
            if(self.IsSet(field) and field != 1):
                self.BuildField(field)
                
        return self.iso
    
    
    def IsSet(self, field):
        if field in self.Bitmap.keys() and self.Bitmap[field] == 1:
            return True
        else:
            return False
        
    def SetField(self, field):
        self.Bitmap[field] = 1
        
    def ResetField(self, field):
        self.Bitmap[field] = 0
    
    def GetMTI(self):
        return self.MTI
    
    def GetBitmap(self):
        return self.Bitmap
    
    def GetDescription(self, field):
        return self.DataTypes[field]['Description']
    
    
    def GetDataType(self, field):
        if(field in ('Bitmap', 'MTI')):
            return self.HeaderDataTypes[field]['DataType']
        else:
            return self.DataTypes[field]['DataType']
    
    def SetDataType(self, field, DataType):
        if(field not in self.DataTypes and field not in ('Bitmap', 'MTI')):
            raise SpecError("Cannot set DataType: Missing field specification")
        
        if(DataType not in DT):
            raise SpecError("Cannot set DataType: Invalid data type")

        if(field == 'MTI' and DataType == DT.BIN):
            raise SpecError("Cannot set DataType: Invalid data type")
        
        if(field == 'Bitmap' and DataType == DT.BCD):
            raise SpecError("Cannot set DataType: Invalid data type")
        
        if(field in ('Bitmap', 'MTI')):
            self.HeaderDataTypes[field]['DataType'] = DataType
        else:
            self.DataTypes[field]['DataType'] = DataType
    
    
    def GetContentType(self, field):
        return self.DataTypes[field]['ContentType']
    
    def SetContentType(self, field, ContentType):
        if(field not in self.DataTypes):
            raise SpecError("Cannot set ContentType: Missing field specification")
        
        if(ContentType not in self.ValidContentTypes):
            raise SpecError("Cannot set ContentType: Invalid Content Type")
        
        self.DataTypes[field]['ContentType'] = ContentType
    

    
    def SetIsoContent(self, iso):
        self.iso = iso
        self.ParseIso()
    
    
    def PrintMessage(self):
        print("MTI:    [{0}]".format(self.MTI))
        
        print "Fields: [",
        for i in sorted(self.FieldData.keys()):
            print str(i),
        print "]"

        for i in sorted(self.FieldData.keys()):
            print("\t{0:02d} - {1: <40} : [{2}]".format(i, self.GetDescription(i), self.FieldData[i]))
         
        
        