

######### ERROR CHECKING
## Bad Mnemonic
## Using the same label twice
## Undefined labels
## Addressing Mode Errors
##    Relative addressing impossible on format 3.

from math import *
import sys

Mnemonics = {'START' : ['D',0],
             'END'   : ['D',0],
             'BYTE'  : ['D'],
             'WORD'  : ['D'],
             'RESB'  : ['D'],
             'RESW'  : ['D'],
             'BASE'  : ['D'],
             'ADD'   : ['I',3,0x18,['m']],
             'ADDR'  : ['I',2,0x90,['r','r']],
             'AND'   : ['I',3,0x40,['m']],
             'CLEAR' : ['I',2,0xB4,['r']],             
             'COMP'  : ['I',3,0x28,['m']],
             'COMPR' : ['I',2,0xA0,['r','r']],
             'DIV'   : ['I',3,0x24,['m']],
             'DIVR'  : ['I',2,0x90,['r','r']],
             'HIO'   : ['I',1,0xF4],
             'J'     : ['I',3,0x3C,['m']],             
             'JEQ'   : ['I',3,0x30,['m']],
             'JGT'   : ['I',3,0x34,['m']],             
             'JLT'   : ['I',3,0x38,['m']],             
             'JSUB'  : ['I',3,0x48,['m']],
             'LDA'   : ['I',3,0x00,['m']],             
             'LDB'   : ['I',3,0x68,['m']], 
             'LDCH'  : ['I',3,0x50,['m']],
             'LDF'   : ['I',3,0x70,['m']],
             'LDL'   : ['I',3,0x08,['m']],                          
             'LDS'   : ['I',3,0x6C,['m']],
             'LDT'   : ['I',3,0x74,['m']],
             'LDX'   : ['I',3,0x04,['m']],
             'LPS'   : ['I',3,0xD0,['m']],
             'MUL'   : ['I',3,0x20,['m']],
             'MULR'  : ['I',2,0x98,['r','r']],                          
             'OR'    : ['I',3,0x44,['m']],
             'RD'    : ['I',3,0xD8,['m']],                          
             'RMO'   : ['I',2,0xAC,['r','r']],
             'RSUB'  : ['I',3,0x4C],
             'SHIFTL' : ['I',2,0xA4,['r','n']],
             'SHIFTR' : ['I',2,0xA8,['r','n']],             
             'SIO'   : ['I',1,0xF0],
             'SSK'   : ['I',3,0xEC,['m']],
             'STA'   : ['I',3,0x0C,['m']],
             'STB'   : ['I',3,0x78,['m']],             
             'STCH'  : ['I',3,0x54,['m']],
             'STI'   : ['I',3,0xD4,['m']], 
             'STL'   : ['I',3,0x14,['m']],             
             'STS'   : ['I',3,0x7C,['m']],                          
             'STSW'  : ['I',3,0xE8,['m']],             
             'STT'   : ['I',3,0x84,['m']],             
             'STX'   : ['I',3,0x10,['m']],             
             'SUB'   : ['I',3,0x1C,['m']],             
             'SUBR'  : ['I',2,0x94,['r','r']],             
             'SVC'   : ['I',2,0xB0,['n']],             
             'TD'    : ['I',3,0xE0,['m']],             
             'TIO'   : ['I',1,0xF8],
             'TIX'   : ['I',3,0x2C,['m']],                          
             'TIXR'  : ['I',2,0xB8,['r']],
             'WD'   : ['I',3,0xDC,['m']]}                          


Symtab = {}
Optab = {}
Optab2 = {}
LOCCTR = 0

X = 0

isBase = False
BaseLoc = 0

Flags = 0
NIXBPE = ''

Nbit = 32
Ibit = 16
Xbit = 8
Bbit = 4
Pbit = 2
Ebit = 1

RegisterNumbers = {'A'  : 0, 
                   'X'  : 1,
                   'L'  : 2,
                   'B'  : 3,
                   'S'  : 4,
                   'T'  : 5,
                   'PC' : 8, 
                   'SW' : 9}


def oppositeBit(b):
     """ b is a single char, 0 or 1.  return the other. """
     if int(b):return '0'
     
     return '1'
    
def isExtended(monic):
    return monic[0] == '+'

def baseMnemonic(mnemonic):
     """ return string with any leading + stripped off """  
     if mnemonic[0] == "+": return mnemonic[1:]
     return mnemonic
def baseOperand(operand):
     """ return string with any leading @ or # stripped off """
     if operand[0] == "@" or operand[0] == "#":return operand[1:]

     if operand == 'BUFFER,X': return 'BUFFER'
     
     return operand
def isString(operands):
     return operands[0] == 'C'

def haslabel(c):
    return c==' ' or c=='\t' or c=='\n'

def isComment(c):
    return c=='.'

def isspace(line):
    return false

def padHexEven(string):
    """ string is hexadecimal.  Prepend with '0' if its length is odd. """
    if (len(string)%2):
        return '0'+string
    return string

def multOfFour(bitstring):
    
    return '0' * ((4-len(bitstring)%4)%4) + bitstring

def prependZeroes(num,string):
    """ Prepend with 0 to a given length """
    while (len(string) < num):
        string = '0' + string
    return string

def bityCount(operands):
     if isString(operands):
          return len(makeLiteral(operands))/2
     return 1

def isSymbol(string):
    """ return True iff string is a key in Symtab """
    return string in Symtab.keys()

def error(msg):
    """ print msg and abort the program """
    print msg
    sys.exit(-1)

def setXBP(nie,PC,mode):

     global Flags
     flags = toBaseTen(nie)

     if PC == 'PC':       #P  PC Relative
          Flags += Pbit
     elif PC =='B':       #B  Base Relative
          Flags += Bbit
     if mode == 'I':      #X  Index
          Flags += Xbit

     return toBitString(Flags, 6)

def setNIE(operands='', mnemonic=''):

     global Flags

     if operands[0]=='@':  #N   Indirect
          Flags += Nbit        
     elif operands[0]=='#':#I   Immediate
          Flags += Ibit
     else:
          Flags += Nbit
          Flags += Ibit
          
     if mnemonic[0]=='+':  
          Flags += Ebit    #E   Extended
          
     return toBitString(Flags, 6)
          
def assembledLength(mnemonic,operands):
    """ return the number of bytes required for the assembly of 
        the given instruction. """

    global isBase
    global BaseLoc

    extend = 0
    
    if isExtended(mnemonic):
        mnemonic = baseMnemonic(mnemonic) 
        extend = 1

    dicPage =  Mnemonics[mnemonic]        
    
    if  mnemonic == 'START':
         length = 0
    elif  mnemonic == 'BASE':
         isBase = True
         length = 0
    elif  mnemonic == 'BYTE':
         length = bityCount(operands) 
    elif  mnemonic == 'WORD':
         length = 3
    elif  mnemonic == 'RESB':
         length = int(operands) 
    elif  mnemonic == 'RESW':        
         length = 3 * int(operands)
    else:
         instrLength = dicPage[1]
         length = instrLength + extend
        
    return length


def bitStr2Hex(bitstring):
    """ return a hex representation of a bit string. """

    hexStr = "%X" % int(bitstring, 2)
    
    leadZeros = (len(bitstring)/4) - len(hexStr)
    
    hexStr = ('0' * leadZeros) + hexStr
    
    return hexStr
    
    
def bitStr2Comp(bitstring):
    """ compute and return the 2's complement of bitstring """

    newBitString = ""

    ## Twos Compliment
    
    ## Inverse Bits Create Bit List
    bitList = []
  
    for bit in bitstring:
        bitList.append(oppositeBit(bit))
  
    ## Add 1
    overflow = True
    for i in range(1,len(bitList) + 1):
        if bitList[-i] == '0':
            bitList[-i] = '1'
            overflow = False
            break
        else:
            bitList[-i] = '0'
    
    ## Did I overflow
    if overflow:
        bitList.insert(0,'1') # = ['1'] + bitList

    ## Create BitString from BitList
    for bit in bitList:
        newBitString +=bit 

    return newBitString

def toBaseTen(string):

    base = 0
    power = len(string) - 1
    for num in string:
        if num == '1':
            base += 2**power
        power -= 1
    return base

def decToBin(n):
    if n==0: return ''
    else:
        return decToBin(n/2) + str(n%2)

def toBitString(val, length=8):
    """Build and return a bit string of the given length.  
       val is a signed integer"""    

    ## Create BinaryStr
    binaryStr = decToBin(abs(val))

    ## Add zeros to the front of BinaryStr
    strLen = len(binaryStr)
    leadZero = length - strLen
    for i in range(leadZero):
        binaryStr = '0' + binaryStr

    if val < 0:
         binaryStr = bitStr2Comp(binaryStr) 

    return binaryStr

def makeLiteral(string):
    """ string is C'CCCCCC...' or (hex) X'HHHHHH....'.
        Return a string of bytes that this represents """

    storage = []

    chars = string.split("'")
    if string[0]=='C': # characters:
         storage = [bitStr2Hex(toBitString(ord(c))) for c in chars[1]]
    elif string[0]=='X': #String
         return chars[1]
         
    else:                  #Hex
         hdigs = padHexEven(chars[1]) # Add a leading zero
         for i in range(0,len(chars[1]),2):
              storage.append(chr(eval("0x"+hdigs[i]+hdigs[i+1])))
              
    newString = ""
    for str in storage:
        newString += str

    return newString

def handleRSUB():

     return 0
     


def parseLine(line):
    
    label  = ''
    operands = ''

    if isComment(line[0]) :
        return ['','','',line]
    
    lineWords = line.split()
    if haslabel(line[0]):
         funkyMonics = baseMnemonic(lineWords[0])
         if funkyMonics == "RSUB" or funkyMonics == "HIO" or \
            funkyMonics == "SIO" or funkyMonics == "TIO":         
              mnemonic = lineWords[0]
              
         else:    
              mnemonic,operands = lineWords[0],lineWords[1]    
    else:
         funkyMonics = baseMnemonic(lineWords[1])
         if funkyMonics == "RSUB" or funkyMonics == "HIO" or \
            funkyMonics == "SIO" or funkyMonics == "TIO":

              mnemonic = lineWords[1]
              label = lineWords[0]              

         else:
              label,mnemonic,operands = lineWords[0],lineWords[1],lineWords[2]    

    return (label, mnemonic, operands,'')

def printSymtab():

    for sym in Symtab:
        print "%s\t%04X"%(sym, Symtab[sym])
    return

def printOptab():

    for op in Optab:
        print "%s\t%04X"%(op, Optab[op])
    return

def registers(operands, mnemonic):

      
     opType = Mnemonics[baseMnemonic(mnemonic)][3]

     if opType == ['r','r']:
          r1,r2 = operands.split(',') 
          rest1 = toBitString(RegisterNumbers[r1],4)
          rest2 = toBitString(RegisterNumbers[r2],4)

     elif opType == ['r','n']:
          r1,n1 = operands.split(',') 
          rest1 = toBitString(RegisterNumbers[r1],4)
          rest2 = toBitString(int(n1),4)

     elif opType == ['r']:
          r1    = operands 
          rest1 = toBitString(RegisterNumbers[r1],4)
          rest2 = '0000'
          
     return rest1 + rest2

def setBase(bOperand):
     
     global BaseLoc
     
     BaseLoc = Optab[bOperand]
     isBase = True


def dist4(op):

     return op

def calcBase(op, instrLen):

     pc = BaseLoc
         
     if not op:
          address = (instrLen + BaseLoc)
     else:
          address = op - pc

     if (address < 0) or (address > 4095):
          #ERROR
          error("Too large for Base addressing")

     return address
               
def dist3(nie, op, instrLen,bOP,operands):

     address = 0
     #print nie

     if nie == "110000":
          dressType = 'PC'
          mode = 'D'

          pc = LOCCTR + instrLen
         
          if not (operands in Optab2):
               address = (instrLen + LOCCTR)
            
          else:

               address = op - pc

          if (address < -2048) or (address > 2047):

               if isBase:
                    address = calcBase(op, instrLen)
                    dressType = 'B'
                  
               else:
                    #ERROR
                    error("Too Large for PC and No Base")
          if operands[-2]== ',':
               mode = 'I'
               #address += RegisterNumbers[operands[-1]] #int(operands[-1])

                    
     elif nie == "010000":       # Indexed
          dressType = '#'
          mode = 'D'

          if not (operands in Optab2):
               address = 0

          else:
               pc = LOCCTR + instrLen               
               address = op - pc
          
     elif nie == "100000":       # Indirect   
          dressType = '@'
          mode = 'D'

          if not (operands in Optab2):
               address += op
          else:
               pc = LOCCTR + instrLen               
               address = op - pc          


     return address, dressType, mode

## #Simple
##      if nixbpe == "110000":
##           address = 1
##      elif nixbpe == "110001":
##           address = 2
##      elif nixbpe == "110010":
##           address = 3
##      elif nixbpe == "110100":
##           address = 4
##      elif nixbpe == "111000":
##           address = 5
##      elif nixbpe == "111001":
##           address = 6                    
##      elif nixbpe == "111010":
##           address = 7
##      elif nixbpe == "111100":
##           address = 8

## #Indirect
##      if nixbpe == "100000":
##           address = 1
##      elif nixbpe == "100001":
##           address = 2
##      elif nixbpe == "100010":
##           address = 3
##      elif nixbpe == "100100":
##           address = 4

## #Immediate

##      if nixbpe == "010000":
##           address = 1
##      elif nixbpe == "010001":
##           address = 2
##      elif nixbpe == "010010":
##           address = 3
##      elif nixbpe == "010100":
##           address = 4




def magic(label, mnemonic, operands):

     global LOCCTR
     global Flags
     
     length = assembledLength(mnemonic,operands)

     index = 1    
 
     bMonic = baseMnemonic(mnemonic)
     monic = Mnemonics[bMonic]

     if monic[0] == 'D':

          if mnemonic == 'BASE':
               setBase(baseOperand(operands))

          elif mnemonic == 'BYTE':
               return makeLiteral(operands)
          elif mnemonic == 'WORD':
               return bitStr2Hex(toBitString(int(operands),24))
                              
          elif mnemonic == 'CLEAR':
               RegisterNumbers[operands]
          
         
     else:
                           #operands='', mnemonic='', mode='I', dreSing = 'P' 

          ####### HACKING TIME
          #if mnemonic == 'STCH'  or mnemonic == 'LDCH':
           #    operands = 'BUFFER'
          

          bOptab = baseOperand(operands)
          op = Optab[bOptab]

          #printOptab()
          if True:
               instrBits = toBitString(monic[2],8) 
          else: 
               instrBits = toBitString(op,8) 
              
          if length==1:               
               return instrBits
          elif length==2:
               instrBits = instrBits + registers(operands,mnemonic)
               
          elif length==3:
               nie = setNIE(operands,mnemonic)
               
               ending,PC,mode = dist3(nie,op, length,bOptab,operands)
               endString = toBitString(ending,12)
               
               nixbpe = setXBP(nie,PC,mode)           
               
               instrBits = instrBits[0:6]+ nixbpe + endString

          else:
               nie = setNIE(operands,mnemonic) 
               nixbpe = setXBP(nie,'AA','D')
               endString = toBitString(dist4(op), 20)
               instrBits = instrBits[0:6]+ nixbpe + endString
          Flags = 0 # reset the flags
          return bitStr2Hex(instrBits)
     return ""
     
def passTwo(lines):
     
     global LOCCTR
     
     for line in lines:     
          label, mnemonic, operands,comment = parseLine(line)
          #if comment:
           #    print comment[:-1]
          if mnemonic:
               if baseMnemonic(mnemonic) == 'RSUB':
                    instruLen = '4F0000'
               elif baseMnemonic(mnemonic) == 'HIO':
                    instruLen = ''
               elif baseMnemonic(mnemonic) == 'SIO':
                    instruLen = ''
               elif baseMnemonic(mnemonic) == 'TIO':
                    instruLen = ''
               else:
                    baseOp = baseOperand(operands)
                    #Check Symbol table
                    if (baseOp in Symtab):
                         Optab[baseOp] = Symtab[baseOperand(operands)]
                         Optab2[baseOp] = Symtab[baseOperand(operands)] 
                    else:
                         Optab[baseOp] = 0
                         #LOCCTR += assembledLength(mnemonic, operands)
                    instruLen = magic(label, mnemonic, operands)
                    
               print "%04X\t%s\t%s\t%s\t%s"%(LOCCTR, label, mnemonic, operands, instruLen)
               LOCCTR += assembledLength(mnemonic, operands)
     return
def passOne(lines):
     
     global LOCCTR
     
     for line in lines:     
          label, mnemonic, operands,comment = parseLine(line)
          
          if mnemonic:
            
               if label:
                    Symtab[label] = LOCCTR 
                    
               #print "%04X\t%s\t%s\t %s"%(LOCCTR,label, mnemonic, operands)
               LOCCTR += assembledLength(mnemonic, operands)
     LOCCTR = 0
     return

def main():

     global sys

     file = sys.argv[1] 
     lines = open(file).readlines()

     passOne(lines)
     #printOptab()

     passTwo(lines)
     

################################################
##    bytes = [mOperandValue("X'"+instr[i:i+2]) 
##                  for i in range(0,len(instr),2)]

##     bytes = []
##     for i in range(0,len(instr),2):
##          bytes.append(mOperandValue("X'"+instr[i:i+2]))

##     inFile = sys.argv[1]
##     lines = readFile(inFile)
##     dotPos = inFile.find('.')
##     exeFile = inFile[:dotPos]+".exe"
##     outF = open(exeFile,'w')
#################################################
    

#    print "\n\n\n\n "

    
#    print "%X" % int(48+3)

#    print "\n\n\n\n "
    #print Symtab
#    printSymtab()
##     printOptab()

##     print bitStr2Comp("0000")
##     print oppositeBit(0)
##     print toBaseTen("00010000")
##     print 4 - (19 % 4)
##     print multOfFour('110000111100001111')
##     bitstring = '00001111'
##     print bitstring[(0*4):(0*4)+4]
##     print "%X" % int('11111111', 2)

##     print bitStr2Hex(bitstring)
##     print toBitString(61)

##     print "Hello World1"
##     print makeLiteral("C'cs240'")
##     print "Hello World1"

##     print "Hello World2"
##     print makeLiteral("H'414543'")
##     print "Hello World2"
    
##     print [ord(i) for i in "AEC"]

##     print ord('A')
##     print chr(ord('A'))

##     flags = Nbit+Xbit+Pbit
##     nixbpe = toBitString(flags,6)

##     print "Hello World"
##     bitstring = '100001111'
##     print '0' * ((4-len(bitstring)%4)%4) + bitstring
##     print "Hello World"

##     print nixbpe
    


main()
        
