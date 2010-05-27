#!/usr/bin/env python
# copyrighted by sandrogauci <sandro@enablesecurity.com> 2010
# 

import random
import os
from time import sleep, time
from optparse import OptionParser
import logging
import socket
import select 
import sys
import datetime
from lib.tftplib import tftp, tftpstruct
from lib.bruteforcehelper import anotherxrange, getRange
from lib.common import __LICENSE__, __version__
import lib.construct

DESC =    """

   Thief.py downloads files from a tftp server quickly and efficiently
   """


def gen_range(template,myranges):
    for myrange in myranges:
        for i in myrange:
            outstr = template % i
            yield(outstr)

def gen_tftpfilelist(fn):
    f = open(fn,'r')
    while 1:
        line = f.readline().strip()
        if len(line) == 0:
            f.close()
            break
        yield(line)

    
def assemblefiles(dumpfiles,sportmap):
    files = dict()
    for addresses in dumpfiles:
        transferdone = False
        tmpfile = str()
        for part in dumpfiles[addresses]:
            data = dumpfiles[addresses][part] 
            tmpfile += data
            if len(data) < 512:
                transferdone = True
        sport = addresses[1][1]
        fn = sportmap[sport]
        files[(fn,transferdone)]=tmpfile
    return files

def splitpartialfull(dumpfiles):
    partial = dict()
    full = dict()
    for addresses in dumpfiles:
        transferdone = False
        for part in dumpfiles[addresses]:
            data = dumpfiles[addresses][part]
            if len(data) < 512:
                transferdone = True
                break
        if transferdone:
            full[addresses] = dumpfiles[addresses]
        else:
            partial[addresses] = dumpfiles[addresses]
    return full,partial

def dumpnassemble(dumpfiles,sportmap,dstdir,partialdump=True):
    partialfiles = None
    if not partialdump:
        dumpfiles,partialfiles = splitpartialfull(dumpfiles)    
    files = assemblefiles(dumpfiles,sportmap)
    donefiles = list()
    for (fn,done) in files:
        if not os.path.exists(dstdir):
            os.mkdir(dstdir)
        data=files[(fn,done)]
        f=open(os.path.join(dstdir,fn),'wb')
        f.write(data)
        f.close()
        donefiles.append(fn)
    return partialfiles,donefiles
        

class mylist:
    def __init__(self,limit=20):
        self.limit = limit
        self.list = []
    
    def append(self,data):
        if len(self.list) > self.limit-1:
            last = self.list.pop(-1)
            if type(last) == socket.socket:
                last.close()
        self.list.append(data)

def getargs():
    usage = "usage: %prog [options] target\r\n"
    usage += "examples:\r\n"
    usage += "%prog 10.0.0.1\r\n"
    usage += "%prog -p6969  10.0.0.1\r\n"
    parser = OptionParser(usage, version="%prog v"+str(__version__)+DESC+__GPL__)
    parser.add_option('-p',"--port", dest="port", default=69, type="int",
                      help="Destination port")
    parser.add_option('--range','-r', dest="range",
                      help="Range of hex (default) or numeric filenames")
    parser.add_option('--rangetype','-T', dest="rangetype", default="hex",
                      type="choice", choices=["hex","num"],
                      help="Range of hex (default, useful for mac addresses) or num for numeric filenames")
    parser.add_option('--fntemplate',dest="fntemplate", default="SEP%09X.cnf.xml",
                      help="""When the --range option is used, by default it produces
                      filenames for SCCP configuration files using the template
                      SEP%09X.cnf.xml. You can modify this to reflect any template""")
    parser.add_option('--file','-f', dest="filenamesfile",
                      default=os.path.join('data','tftplist.txt'),
                      help="File containing a list of files to download")
    parser.add_option('-o','--output',dest="dstdir", default="download",
                      help="Output directory where the files will be downloaded")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Please pass just one destination tftp server name")
    return (options, args)

    
def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    options,args = getargs()
    dst = (args[0],int(options.port))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    mydirtysocks = mylist(limit=100)
    mydirtysocks.append(s)
    t = tftp()
    if options.range:
        ranges = getRange(options.range,rangetype=options.rangetype)
        filelist = gen_range(options.fntemplate, ranges)
    else:
        filelist = gen_tftpfilelist(options.filenamesfile)
    dumpfiles = dict()
    ackbucket = list()
    sportmap = dict()
    start_time = datetime.datetime.now()
    cleansocks = list()    
    finito = False
    lastrecv = time()
    maxlastrecv = 5
    if not os.path.exists(options.dstdir):
        os.mkdir(options.dstdir)
    while 1:
        socklists = list()
        socklists.extend(mydirtysocks.list)
        socklists.extend(cleansocks)
        r,w,e = select.select(socklists,[],[],0.1)
        if len(r) > 0:        
            for s in r:
                recv = s.recvfrom(1024)
                log.debug('Recv: %s' % `recv`)
                lastrecv = time()
                buff = recv[0]
                ipaddr = recv[1]
                try:
                    response = tftpstruct.parse(buff)
                except lib.construct.core.RangeError:
                    response = None
                if response is None:
                    log.warn('Error parsing response')
                    continue
                if response.operation == 'ERROR':
                    if response.data.errorcode == 'FileNotFound':
                        pass
                    else:
                        log.debug(str(response))
                        log.warn( "Time for a siesta.. I think the tftp can't keep up")
                        sleep(2)
                elif response.operation == 'DATA':
                    addresses = (ipaddr,s.getsockname())
                    if addresses not in dumpfiles:
                        dumpfiles[addresses] = dict()                
                    dumpfiles[addresses][response.data.block] = response.data.data
                    if s in mydirtysocks.list:
                        mydirtysocks.list.remove(s)
                        cleansocks.append(s)
                    ackbucket.append([response.data.block,ipaddr,s])            
        else:
            if time() - lastrecv > maxlastrecv:
                log.error('Did not receive a response for %s seconds, quitting' \
                          % (time()-lastrecv))
                finito = True
            if len(ackbucket) > 0:
                block,datadst,s = ackbucket.pop(-1)
                data = t.makeack(block)                
                s.sendto(data,datadst)
            elif finito:
                break
            if not finito:
                try:
                    fn = filelist.next()
                except StopIteration:
                    finito = True
                    continue
                data = t.makerrq(fn)
                log.debug('asking for %s' % fn)
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(5)
                s.sendto(data,dst)
                mydirtysocks.append(s)        
                saddr,sport = s.getsockname()
                sportmap[sport] = fn
            if random.randrange(84) == 42:
                dumpfiles,files = dumpnassemble(dumpfiles,sportmap,options.dstdir,partialdump=False)
                for fn in files:
                    log.info("Dumped %s" % fn)
    
    dumpfiles,files = dumpnassemble(dumpfiles,sportmap,options.dstdir,partialdump=True)
    for fn in files:
        log.info( "pos 2 Dumped %s" % fn)
    log.info( "Total time: %s" % (datetime.datetime.now() - start_time) )

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()