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
class BuildError(Exception):
        def __init__(self, value):
                self.str = value
        def __str__(self):
                return repr(self.str)
            
            
import py8583spec    
class Iso8583:

    
    ValidContentTypes = ('a', 'n', 's', 'an', 'as', 'ns', 'ans', 'b', 'z')

    Strict = False
    
    __Bitmap = {}
    __FieldData = {}
    
    def Strict(self, Value):
        if(Value != True and Value != False):
            raise ValueError
        self.Strict = Value
    
    
    def __init__(self,IsoMsg = None, IsoSpec = None):
        
        if(IsoSpec != None):
            self.__IsoSpec = IsoSpec
        else:
            self.__IsoSpec = py8583spec.IsoSpec1987ASCII()
        
        if(IsoMsg != None):
            self.iso = IsoMsg
            self.ParseIso()
            
    def SetIsoContent(self, iso):
        self.iso = iso
        self.ParseIso()
    
    
    
    def ParseMTI(self, p):
        DataType = self.__IsoSpec.DataType('MTI')
        
        if(DataType == DT.BCD):
            self.__MTI = Bcd2Str(self.iso[p:p+2])
            p+=2
        elif(DataType == DT.ASCII):
            self.__MTI = self.iso[p:p+4]
            p+=4
        
        try: # MTI should only contain numbers
            int(self.__MTI)
        except:
            raise ParseError("Invalid MTI: [{0}]".format(self.__MTI))
            
        if(self.Strict == True):
            if(self.__MTI[1] == '0'):
                raise ParseError("Invalid MTI: Invalid Message type [{0}]".format(self.__MTI))
                  
            if(int(self.__MTI[3]) > 5):
                raise ParseError("Invalid MTI: Invalid Message origin [{0}]".format(self.__MTI))
        
        return p
    
    
    def ParseBitmap(self, p):
        DataType = self.__IsoSpec.DataType(1)

        if(DataType == DT.BIN):
            Primary = self.iso[p:p+8]
            p += 8
        elif(DataType == DT.ASCII):
            Primary = binascii.unhexlify(self.iso[p:p+16])
            p += 16
                
        IntPrimary = struct.unpack_from("!Q", Primary)[0]
        
        for i in range(1, 65):
            self.__Bitmap[i] = (IntPrimary >> (64 - i)) & 0x1

        if(self.__Bitmap[1] == 1):
            if(DataType == DT.BIN):
                Secondary = self.iso[p:p+8]
                p += 8
            elif(DataType == DT.ASCII):
                Secondary = binascii.unhexlify(self.iso[p:p+16])
                p += 16
                
            IntSecondary = struct.unpack_from("!Q", Secondary)[0]
            
            for i in range(1, 65):
                self.__Bitmap[i+64] = (IntSecondary >> (64 - i)) & 0x1
            
        return p
            
            
    def ParseField(self, field, p):
        
        try:
            DataType = self.__IsoSpec.DataType(field)
            LenType = self.__IsoSpec.LengthType(field)
            ContentType = self.__IsoSpec.ContentType(field)
            MaxLength = self.__IsoSpec.MaxLength(field)
        except:
            raise SpecError("Cannot parse F{0}: Incomplete field specification".format(field))

        try:
            if(DataType == DT.ASCII and ContentType == 'b'):
                MaxLength *= 2
                
            if(LenType == LT.FIXED):
                Len = MaxLength
            elif(LenType == LT.LVAR):
                pass
            elif(LenType == LT.LLVAR):
                LenDataType = self.__IsoSpec.LengthDataType(field)
                if(LenDataType == DT.ASCII):
                    Len = int(self.iso[p:p+2])
                    p+=2
                elif(LenDataType == DT.BCD):
                    Len = Bcd2Int(self.iso[p:p+1])
                    p+=1
            elif(LenType == LT.LLLVAR):
                LenDataType = self.__IsoSpec.LengthDataType(field)
                if(LenDataType == DT.ASCII):
                    Len = int(self.iso[p:p+3])
                    p+=3
                elif(LenDataType == DT.BCD):
                    Len = Bcd2Int(self.iso[p:p+2])
                    p+=2
        except ValueError:
            raise ParseError("Cannot parse F{0}: Invalid length".format(field))
            
        if(Len > MaxLength):
            raise ParseError("F{0} is larger than maximum length ({1}>{2})".format(field, Len, MaxLength))
        

        try:
            if(DataType == DT.ASCII):
                if(ContentType == 'n'):
                    self.__FieldData[field] = int(self.iso[p:p+(Len)])
                else:
                    self.__FieldData[field] = self.iso[p:p+(Len)]
                p += Len
            elif(DataType == DT.BCD):
                if(Len % 2 == 1):
                    Len += 1
                if(ContentType == 'n'):
                    self.__FieldData[field] = Bcd2Int(self.iso[p:p+(Len/2)])
                elif(ContentType == 'z'):
                    self.__FieldData[field] = binascii.hexlify(self.iso[p:p+(Len/2)]).upper()
                p += Len/2
            elif(DataType == DT.BIN):
                self.__FieldData[field] = binascii.hexlify(self.iso[p:p+(Len)]).upper()
                p += Len
        except:
            raise ParseError("Cannot parse F{0}".format(field))
        
        if(ContentType == 'z'):
            self.__FieldData[field] = self.__FieldData[field].replace("D", "=") # in track2, replace d with =  
            self.__FieldData[field] = self.__FieldData[field].replace("F", "") # in track2, remove trailing f
 
        return p
    
    
    def ParseIso(self):
        p = 0
        p = self.ParseMTI(p)
        p = self.ParseBitmap(p)


        for field in self.__Bitmap:
            if(self.Field(field) == 1):
                p = self.ParseField(field, p)
    
    
    



    def BuildMTI(self):
        if(self.__IsoSpec.DataType('MTI') == DT.BCD):
            self.iso += Str2Bcd(self.__MTI)
        elif(self.__IsoSpec.DataType('MTI') == DT.ASCII):
            self.iso += self.__MTI
    
    
    def BuildBitmap(self):
        DataType = self.__IsoSpec.DataType(1)
        
        IntPrimary = 0
        for i in range(1, 65):
            IntPrimary |= (self.__Bitmap[i] & 0x1) << (64 - i)

        Primary = struct.pack("!Q", IntPrimary)

        if(DataType == DT.BIN):
            self.iso += Primary
        elif(DataType == DT.ASCII):
            self.iso += binascii.hexlify(Primary)
            
            
    def BuildField(self, field):
        try:
            DataType = self.__IsoSpec.DataType(field)
            LenType = self.__IsoSpec.LengthType(field)
            ContentType = self.__IsoSpec.ContentType(field)
            MaxLength = self.__IsoSpec.MaxLength(field)
        except:
            raise SpecError("Cannot parse F{0}: Incomplete field specification".format(field))
 

        data = ""
        if(LenType == LT.FIXED):
            Len = MaxLength
            
            if(ContentType == 'n'):
                formatter = "{{0:0{0}d}}".format(Len)
            elif('a' in ContentType or 'n' in ContentType or 's' in ContentType):
                formatter = "{{0: >{0}}}".format(Len)
            else:
                formatter = "{0}"
                
            data = formatter.format(self.__FieldData[field])
                
        else:
            LenDataType = self.__IsoSpec.LengthDataType(field)
            
            data = "{0}".format(self.__FieldData[field])
            Len = len(data)
            if(DataType == DT.BIN):
                Len /=2
                
            if(Len > MaxLength):
                raise BuildError("Cannot Build F{0}: Field Length larger than specification".format(field))
            
            if(LenType == LT.LVAR):
                LenData = "{0:01d}".format(Len)
                
            elif(LenType == LT.LLVAR):
                LenData = "{0:02d}".format(Len)
                
            elif(LenType == LT.LLLVAR):
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
            self.iso += binascii.unhexlify(self.__FieldData[field])


    def BuildIso(self):
        self.iso = ""
        self.BuildMTI()
        self.BuildBitmap()
        
        for field in self.__Bitmap:
            if(self.Field(field) == 1):
                self.BuildField(field)
                
        return self.iso
    
    
    

        
    def Field(self, field, Value = None):
        if(Value == None):
            try:
                return self.__Bitmap[field]
            except KeyError:
                return 0
        else:
            self.__Bitmap[field] = Value 
            

    def FieldData(self, field, Value = None):
        if(Value == None):
            try:
                return self.__FieldData[field]
            except KeyError:
                return 0
        else:
            self.__FieldData[field] = Value 
            
            
    def Bitmap(self):
        return self.__Bitmap    

    def MTI(self, MTI = None):
        if(MTI == None):
            return self.__MTI
        else:
            try: # MTI should only contain numbers
                int(MTI)
            except:
                raise SpecError("Invalid MTI [{0}]: MTI must contain only numbers".format(MTI))
        
            if(self.Strict == True):
                if(MTI[1] == '0'):
                    raise SpecError("Invalid MTI [{0}]: Invalid Message type".format(MTI))
                      
                if(int(MTI[3]) > 5):
                    raise SpecError("Invalid MTI [{0}]: Invalid Message origin".format(MTI))
            
            self.__MTI = MTI


    def Description(self, field, Description = None):
        return self.__IsoSpec.Description(field, Description)
    
    def DataType(self, field, DataType = None):
        return self.__IsoSpec.DataType(field, DataType)
    
    def ContentType(self, field, ContentType = None):
        return self.__IsoSpec.ContentType(field, ContentType)



    def PrintMessage(self):
        print("MTI:    [{0}]".format(self.__MTI))
        
        print "Fields: [",
        for i in sorted(self.__Bitmap.keys()):
            if(i == 1): 
                continue
            if(self.__Bitmap[i] == 1):
                print str(i),
        print "]"

        for i in sorted(self.__Bitmap.keys()):
            if(i == 1): 
                continue
            if(self.__Bitmap[i] == 1):
                print("\t{0:02d} - {1: <41} : [{2}]".format(i, self.__IsoSpec.Description(i), self.__FieldData[i]))

