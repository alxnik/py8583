from .py8583 import DT, LT, SpecError
    

            
class IsoSpec(object):
    __ValidContentTypes = ('a', 'n', 's', 'an', 'as', 'ns', 'ans', 'b', 'z')
    
    Descriptions = {}
    ContentTypes = {}
    DataTypes = {}
    
    def __init__(self):
        self.SetDescriptions()
        self.SetContentTypes()
        self.SetDataTypes()
    
    def SetDescriptions(self):
        pass
    def SetContentTypes(self):
        pass
    def SetDataTypes(self):
        pass
         
    def Description(self, field, Description = None):
        if(Description == None):
            return self.Descriptions[field]
        else:
            self.Descriptions[field] = Description

    def DataType(self, field, DataType = None):
        if(DataType == None):
            return self.DataTypes[field]['Data']
        else:
            if(DataType not in DT):
                raise SpecError("Cannot set data type '{0}' for F{1}: Invalid data type".format(DataType, field))
            if(field not in self.DataTypes.keys()):
                self.DataTypes[field] = {}
            self.DataTypes[field]['Data'] = DataType
    
    def ContentType(self, field, ContentType = None):
        if(ContentType == None):
            return self.ContentTypes[field]['ContentType']
        else:
            if(ContentType not in self.__ValidContentTypes):
                raise SpecError("Cannot set Content type '{0}' for F{1}: Invalid content type".format(ContentType, field))
            self.ContentTypes[field]['ContentType'] = ContentType
            
    def MaxLength(self, field, MaxLength = None):
        if(MaxLength == None):
            return self.ContentTypes[field]['MaxLen']
        else:
            self.ContentTypes[field]['MaxLen'] = MaxLength
    
    def LengthType(self, field, LengthType = None):
        if(LengthType == None):
            return self.ContentTypes[field]['LenType']
        else:
            if(LengthType not in self.__ValidContentTypes):
                raise SpecError("Cannot set Length type '{0}' for F{1}: Invalid length type".format(LengthType, field))
            self.ContentTypes[field]['LenType'] = LengthType
    
    def LengthDataType(self, field, LengthDataType = None):
        if(LengthDataType == None):
            return self.DataTypes[field]['Length']
        else:
            if(LengthDataType not in DT):
                raise SpecError("Cannot set data type '{0}' for F{1}: Invalid data type".format(LengthDataType, field))
            if(field not in self.DataTypes.keys()):
                self.DataTypes[field] = {}
            self.DataTypes[field]['Length'] = LengthDataType
    
    
    
class IsoSpec1987(IsoSpec):
    def SetDescriptions(self):
        self.Descriptions = Descriptions['1987']
    def SetContentTypes(self):
        self.ContentTypes = ContentTypes['1987']
        
class IsoSpec1987ASCII(IsoSpec1987):
    def SetDataTypes(self):
        self.DataType('MTI', DT.ASCII)
        self.DataType(1, DT.ASCII) # bitmap
        
        for field in self.ContentTypes.keys():
            self.DataType(field, DT.ASCII)
            if(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.ASCII)
                
class BICISO(IsoSpec1987ASCII):
    def SetContentTypes(self):
        super(BICISO, self).SetContentTypes()
        
        # Variations between official ISO and BIC ISO
        self.ContentTypes[41]['MaxLen'] = 16
        self.ContentTypes[44]['MaxLen'] = 27
                
class IsoSpec1987BCD(IsoSpec1987):
    def SetDataTypes(self):
        self.DataType('MTI', DT.BCD)
        self.DataType(1, DT.BIN) # bitmap 
        
        # Most popular BCD implementations use the reserved/private fields
        # as binary, so we have to set them as such in contrast to the ISO spec
        for field in self.ContentTypes.keys():
            if(self.MaxLength(field) == 999):
                self.ContentType(field, 'b')
        
        
        for field in self.ContentTypes.keys():
            
            ContentType = self.ContentType(field)
            
            if('a' in ContentType or 's' in ContentType):
                self.DataType(field, DT.ASCII)
            elif(ContentType == 'b'):
                self.DataType(field, DT.BIN)
            else:
                self.DataType(field, DT.BCD)

            if(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.BCD)

Descriptions = {}

Descriptions['1987'] = {
    1 : 'Bitmap' ,
    2 : 'Primary account number (PAN)' ,
    3 : 'Processing code' ,
    4 : 'Amount, transaction' ,
    5 : 'Amount, settlement' ,
    6 : 'Amount, cardholder billing' ,
    7 : 'Transmission date & time' ,
    8 : 'Amount, cardholder billing fee' ,
    9 : 'Conversion rate, settlement' ,
    10 : 'Conversion rate, cardholder billing' ,
    11 : 'System trace audit number' ,
    12 : 'Time, local transaction (hhmmss)' ,
    13 : 'Date, local transaction (MMDD)' ,
    14 : 'Date, expiration' ,
    15 : 'Date, settlement' ,
    16 : 'Date, conversion' ,
    17 : 'Date, capture' ,
    18 : 'Merchant type' ,
    19 : 'Acquiring institution country code' ,
    20 : 'PAN extended, country code' ,
    21 : 'Forwarding institution. country code' ,
    22 : 'Point of service entry mode' ,
    23 : 'Application PAN sequence number' ,
    24 : 'Network International identifier (NII)' ,
    25 : 'Point of service condition code' ,
    26 : 'Point of service capture code' ,
    27 : 'Authorizing identification response length' ,
    28 : 'Amount, transaction fee' ,
    29 : 'Amount, settlement fee' ,
    30 : 'Amount, transaction processing fee' ,
    31 : 'Amount, settlement processing fee' ,
    32 : 'Acquiring institution identification code' ,
    33 : 'Forwarding institution identification code' ,
    34 : 'Primary account number, extended' ,
    35 : 'Track 2 data' ,
    36 : 'Track 3 data' ,
    37 : 'Retrieval reference number' ,
    38 : 'Authorization identification response' ,
    39 : 'Response code' ,
    40 : 'Service restriction code' ,
    41 : 'Card acceptor terminal identification' ,
    42 : 'Card acceptor identification code' ,
    43 : 'Card acceptor name/location' ,
    44 : 'Additional response data' ,
    45 : 'Track 1 data' ,
    46 : 'Additional data - ISO' ,
    47 : 'Additional data - national' ,
    48 : 'Additional data - private' ,
    49 : 'Currency code, transaction' ,
    50 : 'Currency code, settlement' ,
    51 : 'Currency code, cardholder billing' ,
    52 : 'Personal identification number data' ,
    53 : 'Security related control information' ,
    54 : 'Additional amounts' ,
    55 : 'Reserved ISO' ,
    56 : 'Reserved ISO' ,
    57 : 'Reserved national' ,
    58 : 'Reserved national' ,
    59 : 'Reserved national' ,
    60 : 'Reserved national' ,
    61 : 'Reserved private' ,
    62 : 'Reserved private' ,
    63 : 'Reserved private' ,
    64 : 'Message authentication code (MAC)' ,
    65 : 'Bitmap, extended' ,
    66 : 'Settlement code' ,
    67 : 'Extended payment code' ,
    68 : 'Receiving institution country code' ,
    69 : 'Settlement institution country code' ,
    70 : 'Network management information code' ,
    71 : 'Message number' ,
    72 : 'Message number, last' ,
    73 : 'Date, action (YYMMDD)' ,
    74 : 'Credits, number' ,
    75 : 'Credits, reversal number' ,
    76 : 'Debits, number' ,
    77 : 'Debits, reversal number' ,
    78 : 'Transfer number' ,
    79 : 'Transfer, reversal number' ,
    80 : 'Inquiries number' ,
    81 : 'Authorizations, number' ,
    82 : 'Credits, processing fee amount' ,
    83 : 'Credits, transaction fee amount' ,
    84 : 'Debits, processing fee amount' ,
    85 : 'Debits, transaction fee amount' ,
    86 : 'Credits, amount' ,
    87 : 'Credits, reversal amount' ,
    88 : 'Debits, amount' ,
    89 : 'Debits, reversal amount' ,
    90 : 'Original data elements' ,
    91 : 'File update code' ,
    92 : 'File security code' ,
    93 : 'Response indicator' ,
    94 : 'Service indicator' ,
    95 : 'Replacement amounts' ,
    96 : 'Message security code' ,
    97 : 'Amount, net settlement' ,
    98 : 'Payee' ,
    99 : 'Settlement institution identification code' ,
    100 : 'Receiving institution identification code' ,
    101 : 'File name' ,
    102 : 'Account identification 1' ,
    103 : 'Account identification 2' ,
    104 : 'Transaction description' ,
    105 : 'Reserved for ISO use' ,
    106 : 'Reserved for ISO use' ,
    107 : 'Reserved for ISO use' ,
    108 : 'Reserved for ISO use' ,
    109 : 'Reserved for ISO use' ,
    110 : 'Reserved for ISO use' ,
    111 : 'Reserved for ISO use' ,
    112 : 'Reserved for national use' ,
    113 : 'Reserved for national use' ,
    114 : 'Reserved for national use' ,
    115 : 'Reserved for national use' ,
    116 : 'Reserved for national use' ,
    117 : 'Reserved for national use' ,
    118 : 'Reserved for national use' ,
    119 : 'Reserved for national use' ,
    120 : 'Reserved for private use' ,
    121 : 'Reserved for private use' ,
    122 : 'Reserved for private use' ,
    123 : 'Reserved for private use' ,
    124 : 'Reserved for private use' ,
    125 : 'Reserved for private use' ,
    126 : 'Reserved for private use' ,
    127 : 'Reserved for private use' ,
    128 : 'Message authentication code'
}
    
ContentTypes = {}

ContentTypes['1987'] = {
    1 :   { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    2 :   { 'ContentType':'n',     'MaxLen': 19,  'LenType': LT.LLVAR },
    3 :   { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    4 :   { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    5 :   { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    6 :   { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    7 :   { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    8 :   { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    9 :   { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    10 :  { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    11 :  { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    12 :  { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    13 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    14 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    15 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    16 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    17 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    18 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    19 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    20 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    21 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    22 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    23 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    24 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    25 :  { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    26 :  { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    27 :  { 'ContentType':'n',     'MaxLen': 1,   'LenType': LT.FIXED },
    28 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    29 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    30 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    31 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    32 :  { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    33 :  { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    34 :  { 'ContentType':'ns',    'MaxLen': 28,  'LenType': LT.LLVAR },
    35 :  { 'ContentType':'z',     'MaxLen': 37,  'LenType': LT.LLVAR },
    36 :  { 'ContentType':'n',     'MaxLen': 104, 'LenType': LT.LLLVAR},
    37 :  { 'ContentType':'an',    'MaxLen': 12,  'LenType': LT.FIXED },
    38 :  { 'ContentType':'an',    'MaxLen': 6,   'LenType': LT.FIXED },
    39 :  { 'ContentType':'an',    'MaxLen': 2,   'LenType': LT.FIXED },
    40 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    41 :  { 'ContentType':'ans',   'MaxLen': 8,   'LenType': LT.FIXED },
    42 :  { 'ContentType':'ans',   'MaxLen': 15,  'LenType': LT.FIXED },
    43 :  { 'ContentType':'ans',   'MaxLen': 40,  'LenType': LT.FIXED },
    44 :  { 'ContentType':'an',    'MaxLen': 25,  'LenType': LT.LLVAR },
    45 :  { 'ContentType':'an',    'MaxLen': 76,  'LenType': LT.LLVAR },
    46 :  { 'ContentType':'an',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    47 :  { 'ContentType':'an',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    48 :  { 'ContentType':'an',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    49 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    50 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    51 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    52 :  { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    53 :  { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    54 :  { 'ContentType':'an',    'MaxLen': 120, 'LenType': LT.LLLVAR},
    55 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    56 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    57 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    58 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    59 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    60 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    61 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    62 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    63 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    64 :  { 'ContentType':'b',     'MaxLen' : 8,  'LenType': LT.FIXED },
    65 :  { 'ContentType' : 'b',   'MaxLen' : 1,  'LenType': LT.FIXED },
    66 :  { 'ContentType' : 'n',   'MaxLen' : 1,  'LenType': LT.FIXED },
    67 :  { 'ContentType' : 'n',   'MaxLen' : 2,  'LenType': LT.FIXED },
    68 :  { 'ContentType' : 'n',   'MaxLen' : 3,  'LenType': LT.FIXED },
    69 :  { 'ContentType' : 'n',   'MaxLen' : 3,  'LenType': LT.FIXED },
    70 :  { 'ContentType' : 'n',   'MaxLen' : 3,  'LenType': LT.FIXED },
    71 :  { 'ContentType' : 'n',   'MaxLen' : 4,  'LenType': LT.FIXED },
    72 :  { 'ContentType' : 'n',   'MaxLen' : 4,  'LenType': LT.FIXED },
    73 :  { 'ContentType' : 'n',   'MaxLen' : 6,  'LenType': LT.FIXED },
    74 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    75 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    76 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    77 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    78 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    79 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    80 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    81 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    82 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    83 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    84 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    85 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    86 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    87 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    88 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    89 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    90 :  { 'ContentType' : 'n',   'MaxLen' : 42, 'LenType': LT.FIXED },
    91 :  { 'ContentType' : 'an',  'MaxLen' : 1,  'LenType': LT.FIXED },
    92 :  { 'ContentType' : 'an',  'MaxLen' : 2,  'LenType': LT.FIXED },
    93 :  { 'ContentType' : 'an',  'MaxLen' : 5,  'LenType': LT.FIXED },
    94 :  { 'ContentType' : 'an',  'MaxLen' : 7,  'LenType': LT.FIXED },
    95 :  { 'ContentType' : 'an',  'MaxLen' : 42, 'LenType': LT.FIXED },
    96 :  { 'ContentType' : 'b',   'MaxLen' : 8,  'LenType': LT.FIXED },
    97 :  { 'ContentType' : 'an',  'MaxLen' : 17, 'LenType': LT.FIXED },
    98 :  { 'ContentType' : 'ans', 'MaxLen' : 25, 'LenType': LT.FIXED },
    99 :  { 'ContentType' : 'n',   'MaxLen' : 11, 'LenType': LT.LLVAR },
    100 : { 'ContentType' : 'n',   'MaxLen' : 11, 'LenType': LT.LLVAR },
    101 : { 'ContentType' : 'ans', 'MaxLen' : 17, 'LenType': LT.LLVAR },
    102 : { 'ContentType' : 'ans', 'MaxLen' : 28, 'LenType': LT.LLVAR },
    103 : { 'ContentType' : 'ans', 'MaxLen' : 28, 'LenType': LT.LLVAR },
    104 : { 'ContentType' : 'ans', 'MaxLen' : 100, 'LenType': LT.LLLVAR },
    105 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    106 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    107 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    108 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    109 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    110 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    111 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    112 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    113 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    114 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    115 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    116 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    117 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    118 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    119 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    120 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    121 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    122 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    123 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    124 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    125 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    126 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    127 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    128 : { 'ContentType' : 'b',   'MaxLen' : 8,  'LenType': LT.FIXED }
}