"""
the Trivial FTP protocol
"""
from construct import *
from construct.text import *

op_code = Enum(UBInt16("operation"),
               RRQ = 1,
               WRQ = 2,
               DATA = 3,
               ACK = 4,
               ERROR = 5
              )

source_file = CString("source_file")
transfer_mode = CString("transfer_mode")
fileoperations = Struct(None,source_file,transfer_mode)
erroroperation = Struct(None,
                        Enum(UBInt16("errorcode"),
                             Unknown = 0,
                             FileNotFound = 1,
                             AccessViolation = 2,
                             DiskFullOrAllocationExceeded = 3,
                             IllegalTftpOperation = 4,
                             UnknownTransferId = 5,
                             FileAlreadyExists = 6,
                             NoSuchUser = 7,
                            ),
                        CString("ErrMsg"))
datapacket = Struct(None,
                    UBInt16("block"),
                    StringAdapter(GreedyRange(Char("data")))
                   )
ackpacket = Struct(None,
                   UBInt16("block"))
tftpstruct = Struct("command",
                      op_code,
                      Switch("data", lambda ctx: ctx["operation"],
                             {
                                'RRQ' : fileoperations,
                                'WRQ' : fileoperations,
                                'DATA' : datapacket,
                                'ACK' : ackpacket,
                                'ERROR' : erroroperation
                             }
                            )
                      )

class tftp:
    def __init__(self,buff=None):
        pass
    
    def parse(self,buff=None):
        tftpstruct.parse(buff)
    
    def makerrq(self,filename,mode='octet'):
        rrq = Container()
        rrq.operation = 'RRQ'
        rrq.data = Container()
        rrq.data.source_file = filename
        rrq.data.transfer_mode = mode
        return tftpstruct.build(rrq)
      
    def makeack(self,block):
         ack = Container()
         ack.operation = 'ACK'
         ack.data = Container()
         ack.data.block = block
         return tftpstruct.build(ack)
        


if __name__ == "__main__":
    cap1 = (
    "000143544c5345503030304432393041423836302e746c76006f6374657400"
    ).decode("hex")

    cap2 = (
    "0005000146696c65206e6f7420666f756e6400"
    ).decode("hex")
    
    cap3 = (
    "000300013c64657669636520207873693a747970653d2261786c3a58495050"
    "686f6e65222063746969643d2232312220757569643d227b64366438393933"
    "362d383162322d623736642d343162632d3337666665323137333139657d22"
    "3e0d0a3c66756c6c436f6e6669673e747275653c2f66756c6c436f6e666967"
    "3e0d0a3c64657669636550726f746f636f6c3e534343503c2f646576696365"
    "50726f746f636f6c3e0d0a3c7373685573657249643e3c2f73736855736572"
    "49643e0d0a3c73736850617373776f72643e3c2f73736850617373776f7264"
    "3e0d0a3c646576696365506f6f6c2020757569643d227b3162316239656236"
    "2d373830332d313164332d626466302d3030313038333032656164317d223e"
    "0d0a3c7265766572745072696f726974793e303c2f7265766572745072696f"
    "726974793e0d0a3c6e616d653e44656661756c743c2f6e616d653e0d0a3c64"
    "61746554696d6553657474696e672020757569643d227b3965633438353061"
    "2d373734382d313164332d626466302d3030313038333032656164317d223e"
    "0d0a3c6e616d653e434d4c6f63616c3c2f6e616d653e0d0a3c646174655465"
    "6d706c6174653e4d2f442f593c2f6461746554656d706c6174653e0d0a3c74"
    "696d655a6f6e653e477265656e77696368205374616e646172642054696d65"
    "3c2f74696d655a6f6e653e0d0a3c2f6461746554"
    ).decode("hex")
    
    cap4 = (
    "00040001123123"
    ).decode("hex")
    caps = [cap1,cap2,cap3,cap4]
    for cap in caps:
        obj = tftpstruct.parse(cap)
        if obj.operation=='ERROR':            
            x = obj.data
            print x.errorcode
    
    t = tftp()
    print t.makerrq('hello.txt')