import binascii
import struct
from enum import IntEnum
import logging

# Data Type enumeration
class DT(IntEnum):
    BCD     = 1
    ASCII   = 2
    BIN     = 3

# Length Type enumeration
class LT(IntEnum):
    FIXED   = 0
    LVAR    = 1
    LLVAR   = 2
    LLLVAR  = 3

class MsgVersion(IntEnum):
    ISO1987  = 0
    ISO1993  = 1
    ISO2003  = 2
    National = 8
    Private  = 9

class MsgClass(IntEnum):
    Authorization     = 1
    Financial         = 2
    FileAction        = 3
    Reversal          = 4
    Reconciliation    = 5
    Administrative    = 6
    FeeCollection     = 7
    NetworkManagement = 8
    Reserved          = 9

class MsgFunction(IntEnum):
    Request         = 0
    RequestResponse = 1
    Advice          = 2
    AdviceResponse  = 3
    Notification    = 4
    NotificationAck = 5
    Instruction     = 6
    InstructionAck  = 7

class MsgOrigin(IntEnum):
    Acquirer       = 0
    AcquirerRepeat = 1
    Issuer         = 2
    IssuerRepeat   = 3
    Other          = 4
    OtherRepeat    = 5



log = logging.getLogger('py8583')


def MemDump(Title, data, size = 16):
    from string import printable as PrintableString
    printable = bytes(PrintableString, 'ascii').replace(b'\r', b'').replace(b'\n', b'') \
                                               .replace(b'\t', b'').replace(b'\x0b', b'') \
                                               .replace(b'\x0c', b'')

    if( isinstance(data, bytes) == False ):
        raise TypeError("Expected bytes for data")

    log.info("{} [{}]:".format(Title, len(data)))
    TheDump = "\n"

    for line in [data[i:i+size] for i in range(0, len(data), size)]:
        
        for c in line:
            try: # python 3
                TheDump += "{:02x} ".format(c) 
            except: # python 2.x
                TheDump += "{:02x} ".format(ord(c))
            
        TheDump += "   " * (size - len(line))
            
        TheDump += ' | '
        for c in line:
            if c in printable:
                TheDump += "{:1c}".format(c)
            else:
                TheDump += '.'
            
        TheDump += "\n"
       
    log.info(TheDump)
    

def Bcd2Str(bcd):
    return binascii.hexlify(bcd).decode('latin')

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
            
            
class Iso8583:
    
    ValidContentTypes = ('a', 'n', 's', 'an', 'as', 'ns', 'ans', 'b', 'z')
    
    
    def __init__(self,IsoMsg = None, IsoSpec = None):
        
        self.strict = False
    
        self.__Bitmap = {}
        self.__FieldData = {}
        self.__iso = b''
        
        if(IsoSpec != None):
            self.__IsoSpec = IsoSpec
        else:
            self.__IsoSpec = py8583spec.IsoSpec1987ASCII()
        
        if(IsoMsg != None):
            if( isinstance(IsoMsg, bytes) == False ):
                raise TypeError("Expected bytes for iso message")
            
            self.__iso = IsoMsg
            self.ParseIso()


    def Strict(self, Value):
        if(Value != True and Value != False):
            raise ValueError
        self.strict = Value

        
    def SetIsoContent(self, IsoMsg):
        if( isinstance(IsoMsg, bytes) == False ):
            raise TypeError("Expected bytes for iso message")
        self.__iso = IsoMsg
        self.ParseIso()
    
    
    
    def ParseMTI(self, p):
        DataType = self.__IsoSpec.DataType('MTI')
        
        if(DataType == DT.BCD):
            self.__MTI = Bcd2Str(self.__iso[p:p+2])
            p+=2
        elif(DataType == DT.ASCII):
            self.__MTI = self.__iso[p:p+4].decode('latin')
            p+=4
        
        try: # MTI should only contain numbers
            int(self.__MTI)
        except:
            raise ParseError("Invalid MTI: [{0}]".format(self.__MTI))
            
        if(self.strict == True):
            if(self.__MTI[1] == '0'):
                raise ParseError("Invalid MTI: Invalid Message type [{0}]".format(self.__MTI))
                  
            if(int(self.__MTI[3]) > 5):
                raise ParseError("Invalid MTI: Invalid Message origin [{0}]".format(self.__MTI))
        
        return p
    
    
    def ParseBitmap(self, p):
        DataType = self.__IsoSpec.DataType(1)

        if(DataType == DT.BIN):
            Primary = self.__iso[p:p+8]
            p += 8
        elif(DataType == DT.ASCII):
            Primary = binascii.unhexlify(self.__iso[p:p+16])
            p += 16
                
        IntPrimary = struct.unpack_from("!Q", Primary)[0]
        
        for i in range(1, 65):
            self.__Bitmap[i] = (IntPrimary >> (64 - i)) & 0x1

        if(self.__Bitmap[1] == 1):
            if(DataType == DT.BIN):
                Secondary = self.__iso[p:p+8]
                p += 8
            elif(DataType == DT.ASCII):
                Secondary = binascii.unhexlify(self.__iso[p:p+16])
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
                    Len = int(self.__iso[p:p+2])
                    p+=2
                elif(LenDataType == DT.BCD):
                    Len = Bcd2Int(self.__iso[p:p+1])
                    p+=1
                else:
                    raise ParseError('Unsupported length data type')
            elif(LenType == LT.LLLVAR):
                LenDataType = self.__IsoSpec.LengthDataType(field)
                if(LenDataType == DT.ASCII):
                    Len = int(self.__iso[p:p+3])
                    p+=3
                elif(LenDataType == DT.BCD):
                    Len = Bcd2Int(self.__iso[p:p+2])
                    p+=2
                else:
                    raise ParseError('Unsupported length data type')
        except ValueError as ex:
            raise ParseError("Cannot parse F{0} - Invalid length: {1}".format(field, ex))
            
        if(Len > MaxLength):
            raise ParseError("F{0} is larger than maximum length ({1}>{2})".format(field, Len, MaxLength))
        
        # In case of zero length, don't try to parse the field itself, just continue
        if(Len == 0):
            if(ContentType == 'n'):
                self.__FieldData[field] = None
            else:
                self.__FieldData[field] = ''
            return p

        try:
            if(DataType == DT.ASCII):
                if(ContentType == 'n'):
                    self.__FieldData[field] = int(self.__iso[p:p+(Len)])
                else:
                    self.__FieldData[field] = self.__iso[p:p+(Len)].decode('latin')
                p += Len
            elif(DataType == DT.BCD):
                if(Len % 2 == 1):
                    Len += 1
                if(ContentType == 'n'):
                    self.__FieldData[field] = Bcd2Int(self.__iso[p:p+(Len//2)])
                elif(ContentType == 'z'):
                    self.__FieldData[field] = binascii.hexlify(self.__iso[p:p+(Len//2)]).decode('latin').upper()
                p += Len//2
            elif(DataType == DT.BIN):
                self.__FieldData[field] = binascii.hexlify(self.__iso[p:p+(Len)]).decode('latin').upper()
                p += Len
        except Exception as ex:
            raise ParseError("Cannot parse F{}: {}".format(field, str(ex))) from None
        
        if(ContentType == 'z'):
            self.__FieldData[field] = self.__FieldData[field].replace("D", "=") # in track2, replace d with =  
            self.__FieldData[field] = self.__FieldData[field].replace("F", "") # in track2, remove trailing f
 
        return p
    
    
    def ParseIso(self):
        p = 0
        p = self.ParseMTI(p)
        p = self.ParseBitmap(p)


        for field in sorted(self.__Bitmap):
            # field 1 is parsed by the bitmap function
            if(field != 1 and self.Field(field) == 1):
                p = self.ParseField(field, p)
    
    
    



    def BuildMTI(self):
        if(self.__IsoSpec.DataType('MTI') == DT.BCD):
            self.__iso += Str2Bcd(self.__MTI)
        elif(self.__IsoSpec.DataType('MTI') == DT.ASCII):
            self.__iso += self.__MTI.encode('latin')
    
    
    def BuildBitmap(self):
        DataType = self.__IsoSpec.DataType(1)
        
        # check if we need a secondary bitmap
        for i in self.__Bitmap.keys():
            if(i > 64):
                self.__Bitmap[1] = 1
                break
        
        IntPrimary = 0
        for i in range(1, 65):
            if i in self.__Bitmap.keys():
                IntPrimary |= (self.__Bitmap[i] & 0x1) << (64 - i)

        Primary = struct.pack("!Q", IntPrimary)

        if(DataType == DT.BIN):
            self.__iso += Primary
        elif(DataType == DT.ASCII):
            self.__iso += binascii.hexlify(Primary).upper()
            
        # Add secondary bitmap if applicable
        if 1 in self.__Bitmap.keys() and self.__Bitmap[1] == 1:
        
            IntSecondary = 0
            for i in range(65, 129):
                if i in self.__Bitmap.keys():
                    IntSecondary |= (self.__Bitmap[i] & 0x1) << (128 - i)
                
            Secondary = struct.pack("!Q", IntSecondary)

            if(DataType == DT.BIN):
                self.__iso += Secondary
            elif(DataType == DT.ASCII):
                self.__iso += binascii.hexlify(Secondary)
            
            
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

            if(ContentType == 'z' and DataType == DT.BIN):
                if(len(data) % 2 == 1):
                    data = data + 'F'

                data = data.replace("=", "D")
                    



            Len = len(data)
            if(DataType == DT.BIN):
                Len //=2
                
            if(Len > MaxLength):
                raise BuildError("Cannot Build F{0}: Field Length larger than specification".format(field))
            
            if(LenType == LT.LVAR):
                LenData = "{0:01d}".format(Len)
                
            elif(LenType == LT.LLVAR):
                LenData = "{0:02d}".format(Len)
                
            elif(LenType == LT.LLLVAR):
                LenData = "{0:03d}".format(Len)
                
            if(LenDataType == DT.ASCII):
                self.__iso += LenData.encode('latin')
            elif(LenDataType == DT.BCD):
                self.__iso += Str2Bcd(LenData)
            elif(LenDataType == DT.BIN):
                self.__iso += binascii.unhexlify(LenData)
            
        
        if(DataType == DT.ASCII):
            self.__iso += data.encode('latin')
        elif(DataType == DT.BCD):
            self.__iso += Str2Bcd(data)
        elif(DataType == DT.BIN):
            self.__iso += binascii.unhexlify(self.__FieldData[field])


    def BuildIso(self):
        self.__iso = b''
        self.BuildMTI()
        self.BuildBitmap()
        
        for field in sorted(self.__Bitmap):
            if(field != 1 and self.Field(field) == 1):
                try:
                    self.BuildField(field)
                except Exception as ex:
                    raise type(ex)('Error building F{}: '.format(field) + repr(ex)) from None

                
        return self.__iso
    
        
    def Field(self, field, Value = None):
        if(Value == None):
            try:
                return self.__Bitmap[field]
            except KeyError:
                return None
        elif(Value == 1 or Value == 0):
            self.__Bitmap[field] = Value
        else:
            raise ValueError 
            

    def FieldData(self, field, Value = None):
        if(Value == None):
            try:
                return self.__FieldData[field]
            except KeyError:
                return None
        else:
            if(len(str(Value)) > self.__IsoSpec.MaxLength(field)):
                raise ValueError('Value length larger than field maximum ({0})'.format(self.__IsoSpec.MaxLength(field)))
            
            self.__FieldData[field] = Value

    def Fields(self):
        return self.__FieldData
            
    def Bitmap(self):
        return self.__Bitmap

    def MTI(self, MTI = None):
        if(MTI == None):
            return self.__MTI
        else:
            MTI = MTI.zfill(4)
            
            if int(MTI[0]) not in list(map(int, MsgVersion)):
                raise ValueError("Invalid MTI [{0}]: Invalid message version".format(MTI))

            if int(MTI[1]) not in list(map(int, MsgClass)):
                raise ValueError("Invalid MTI [{0}]: Invalid message class".format(MTI))

            if int(MTI[2]) not in list(map(int, MsgFunction)):
                raise ValueError("Invalid MTI [{0}]: Invalid message class".format(MTI))

            if int(MTI[3]) not in list(map(int, MsgOrigin)):
                raise ValueError("Invalid MTI [{0}]: Invalid message class".format(MTI))

            self.__MTI = MTI

    def Version(self):
        for i in MsgVersion:
            if int(self.__MTI[0]) == i.value:
                return i

    def Class(self):
        for i in MsgClass:
            if int(self.__MTI[1]) == i.value:
                return i

    def Function(self):
        for i in MsgFunction:
            if int(self.__MTI[2]) == i.value:
                return i

    def Origin(self):
        for i in MsgOrigin:
            if int(self.__MTI[3]) == i.value:
                return i


    def Description(self, field, Description = None):
        return self.__IsoSpec.Description(field, Description)
    
    def DataType(self, field, DataType = None):
        return self.__IsoSpec.DataType(field, DataType)
    
    def ContentType(self, field, ContentType = None):
        return self.__IsoSpec.ContentType(field, ContentType)


    # Due to legacy...
    def PrintMessage(self, level = logging.DEBUG):
        self.DebugMessage(level)

    def DebugMessage(self, level = logging.DEBUG):
        log.log(level, "MTI:    [{0}]".format(self.__MTI))
        
        bitmapLine = "Fields: [ "
        for i in sorted(self.__Bitmap.keys()):
            if(i == 1): 
                continue
            if(self.__Bitmap[i] == 1):
                bitmapLine += str(i) + " "
        bitmapLine += "]"
        log.log(level, bitmapLine)
        

        for i in sorted(self.__Bitmap.keys()):
            if(i == 1): 
                continue
            if(self.__Bitmap[i] == 1):
                
                try:
                    FieldData = self.__FieldData[i]
                except KeyError:
                    FieldData = ''
                
                if(self.ContentType(i) == 'n' and self.__IsoSpec.LengthType(i) == LT.FIXED):
                    FieldData = str(FieldData).zfill(self.__IsoSpec.MaxLength(i))
                    
                log.log(level, "\t{0:>3d} - {1: <41} : [{2}]".format(i, self.__IsoSpec.Description(i), FieldData))
