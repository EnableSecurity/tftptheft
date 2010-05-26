#!/usr/bin/env python

# comments / license
import struct
import socket


def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('!L',socket.inet_aton(ip))[0]

def numToDottedQuad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('!L',n))
                                                                                                             

def ip4range(*args):
    """takes a list ip ranges as an argument and returns a generator object                                                                                                         
    examples accepted:                                                                                                           
        1.1.1.1/16
        1.1.1.1-25
        1.1.1.1-1.1.2.255
        www.google.com/24
                                                                                                     
    """
    for arg in args:                                              
        r = getranges(arg)
        if r is None:                                                                                                   
            continue                                                                                                               
        startip,endip = r
        curip = startip
        while curip <= endip:
            yield(numToDottedQuad(curip))
            curip += 1                                                                                                    

def calcmasksize(ipstring):                                                                                                                         
    """given an ipstring this function returns the number of IPs"""
    tmp = getmaskranges(ipstring)                                                                
    if tmp is not None:
        naddr1,naddr2 = tmp
        size = naddr2 - naddr1 + 1
        return size                                                                                                                

def getranges(ipstring):
    """
    Tries to get a range of ip addresses based on a string
    supports the following formats:
     -  1.2.3.4-1.2.4.5
     -  1-2.3.4.5-9
     -  www.test.com/24
     -  1.2.3.4/24
     -  hostname
     
    >>> getranges('127.0.0.1')
    (2130706433, 2130706433)
    
    >>> getranges('1-2.3.4.5-9')
    (16974853, 33752073)
    
    >>> getranges('localhost/24')
    (2130706433L, 2130706686L)
    
    >>> getranges('127.0.0.1-127.0.0.255')
    (2130706433, 2130706687)
    
    >>> getranges('127.0.0.1/24')
    (2130706433L, 2130706686L)
    
    >>> getranges('localhost')
    (2130706433, 2130706433)
    
    >>> getranges('127.0.0.*')
    (2130706432, 2130706687)
    """
    import re
    from socket import gethostbyname                                                                                                                  
    if re.match(                                                                                                     
        '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
        ipstring                                                                                                             
        ):
        naddr1,naddr2 = map(dottedQuadToNum,ipstring.split('-'))
    elif re.match(                                                                                                         
        '^(\d{1,3}(-\d{1,3})*)\.(\*|\d{1,3}(-\d{1,3})*)\.(\*|\d{1,3}(-\d{1,3})*)\.(\*|\d{1,3}(-\d{1,3})*)$',
        ipstring
        ):                                                                                                     
        naddr1,naddr2 = map(dottedQuadToNum,getranges2(ipstring))
    elif re.match(                                                                                                                  
        '^.*?\/\d{,2}$',
        ipstring
        ):
        r = getmaskranges(ipstring)
        if r is None:                                                                                                     
            return
        naddr1,naddr2 = r                                                                                                       
    else:
        # we attempt to resolve the host
        try:                                                                                                            
            naddr1 = dottedQuadToNum(gethostbyname(ipstring))
            naddr2 = naddr1
        except socket.error:
            ("sip",'Could not resolve %s' % ipstring)
            return                                                                                                               
    return((naddr1,naddr2))

def getranges2(ipstring):                                                                                                  
    _tmp = ipstring.split('.')                                                                                                 
    if len(_tmp) != 4:
        raise ValueError, "needs to be a Quad dotted ip"
    _tmp2 = map(lambda x: x.split('-'),_tmp)                                                                                                            
    startip = list()
    endip = list()
    for dot in _tmp2:
        if dot[0] == '*':                                              
            startip.append('0')
            endip.append('255')
        elif len(dot) == 1:
            startip.append(dot[0])                                                                                                   
            endip.append(dot[0])
        elif len(dot) == 2:
            startip.append(dot[0])
            endip.append(dot[1])
    naddr1 = '.'.join(startip)                                                                                                               
    naddr2 = '.'.join(endip)
    return(naddr1,naddr2)


def getmaskranges(ipstring):
    """gets the lower and upper ip address when given a mask
    
    >>> getmaskranges('127.0.0.1/32')
    (2130706433, 2130706433)
    
    >>> getmaskranges('127.0.0.1/24')
    (2130706433L, 2130706686L)
    
    >>> getmaskranges('1.1.1.1/24')
    (16843009L, 16843262L)
    """
    import re
    from socket import gethostbyname
    addr,mask = ipstring.rsplit('/',1)
    if not re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',addr):
        try:            
            addr = gethostbyname(addr)
        except socket.error:
            return

    naddr = dottedQuadToNum(addr)
    masklen = int(mask)
    if masklen==32:
        return(naddr,naddr)
    if not 0 <= masklen <= 32:
        raise ValueError
    naddr1 = naddr & (((1<<masklen)-1)<<(32-masklen)) + 1
    naddr2 = naddr1 + (1<<(32-masklen)) - 3
    return (naddr1,naddr2)


def getlocalip():
    try:
        myip = socket.gethostbyname(socket.gethostname())
    except socket.error:
        #log.error("could not retrieve the local ip address - please specify via the -x option")
        return
    return myip


def mysendto(sock,data,dst):
    """A sendto replacement which splits up large packets into smaller 8192b packets

    Arguments:
    sock -- a socket object
    data -- the data arg to pass to sock.sendto
    dst -- the destination (ip,port) tuple to pass to sock.sendto

    """
    sock.connect(dst)
    while data:
        #if socknode.nodetype == 'LocalNode':
            #bytes_sent = sock.sendto(data[:8192],dst)
            #data = data[bytes_sent:]
        bytes_sent = sock.send(data[:8192])
        data = data[bytes_sent:]



def bindto(bindingip,startport,s):
    """Binds to a specific port and port. If the port is not available, then increments
    until a free port is found.

    Arguments:
    bindingip -- a string containing an IP address
    startport -- the prefered port to bind to
    s -- socket object

    """
    localport = startport
    #devlog("sip","binding to %s:%s" % (bindingip,localport))
    while 1:
        if localport > 65535:
            ("sip","Could not bind to any port")
            return
        try:
            s.bind((bindingip,localport))
            break
        except socket.error:
            #devlog("sip","could not bind to %s:%s" % (bindingip,localport))
            localport += 1
    return localport,s


def scanlist(iprange,portranges,methods):
    """ a generator that iterates on a range of ip addresses and ports and methods
    """
    for ip in iter(iprange):
        for portrange in portranges:
            for port in portrange:
                for method in methods:
                    yield(ip,port,method)

if __name__ == "__main__":
    import doctest
    doctest.testmod()