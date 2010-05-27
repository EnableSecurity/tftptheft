#!/usr/bin/env python
# copyrighted by sandrogauci <sandro@enablesecurity.com> 2010
# 

import socket
import select 
import sys
import datetime
import random
from lib.tftplib import tftp, tftpstruct
from lib.iphelper import ip4range
import random
import os
from lib.common import __LICENSE__, __version__
from time import sleep
import logging
from optparse import OptionParser

DESC =    """

   Finder.py finds tftp servers quickly
    """


def getargs():
    usage = "usage: %prog [options] target\r\n"
    usage += "examples:\r\n"
    usage += "%prog 10.0.0.1/18 192.168.2.1/24\r\n"
    usage += "%prog -p6969  10.0.0.1/24\r\n"
    parser = OptionParser(usage, version="%prog v"+str(__version__)+DESC+__GPL__)
    parser.add_option("--port", '-p', dest="port", default=69, type="int",
                      help="Destination port")
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("Please pass some ip ranges")
    return (options, args)

def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    options,args = getargs()
    ipranges = ip4range(*args)
    port = options.port
    fn = str(random.randrange(1000,9999)) + '.xml'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(5)
    t = tftp()
    start_time = datetime.datetime.now()
    finito = False
    data = t.makerrq(fn)
    while 1:
        r,w,e = select.select([s],[],[],0.1)
        if len(r) > 0:        
            for s in r:
                try:
                    recv = s.recvfrom(1024)
                except socket.error,e:
                    print e
                    continue            
                buff = recv[0]
                ipaddr = recv[1]
                try:
                    response = tftpstruct.parse(buff)
                except Exception,e:
                    print e
                log.info("IP: %s:%s responded: %s" % (ipaddr[0],ipaddr[1],response))
        else:
            if finito:
                break
            if not finito:
                try:
                    dst = ipranges.next(),port
                except StopIteration:
                    finito = True
                    continue
                try:
                    log.debug('sending to %s:%s' % dst)
                    s.sendto(data,dst)
                except socket.error, err:
                    log.warn('Socket error: %s %s' % (dst,err))
                    
    
    log.info("Duration: %s" %  (datetime.datetime.now() - start_time))

if __name__ == "__main__":
    logging.basicConfig()
    main()