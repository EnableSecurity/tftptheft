#!/usr/bin/env python
from datetime import datetime
def calcgenerator(gen):
    i = 0
    for g in gen:
        i+=1
    return i


def getRange(rangestr,rangetype='num'):
    xrange = anotherxrange
    assert rangetype in ['num','hex']
    _tmp1 = rangestr.split(',')
    numericrange = list()
    for _tmp2 in _tmp1:
        _tmp3 = _tmp2.split('-',1)
        if rangetype == 'hex':
            _tmp3 = map(lambda x: str(int(x,16)), _tmp3)
        if len(_tmp3) > 1:
            if not (_tmp3[0].isdigit() or _tmp3[1].isdigit()):                
                raise ValueError, "the ranges need to be digits"
                return            
            startport,endport = map(int,[_tmp3[0],_tmp3[1]])
            endport += 1
            numericrange.append(xrange(startport,endport))
        else:
            if not _tmp3[0].isdigit():
                raise ValueError, "the ranges need to be digits"                
                return
            singleport = int(_tmp3[0])
            numericrange.append(xrange(singleport,singleport+1))
    return numericrange


def extensiongenerator(defaults=True,extrange='',dictionary=None,customlist=[],template=None):
    if len(extrange) > 0:
        for genrange in getRange(extrange):                                    
            if not template:
                template = '%i'
            for i in genrange:
                yield(template % i)

    if dictionary is not None:
        if len(dictionary) > 0:
            f=open(dictionary,'r')
            newline = 'hmm'                                                                                                         
            while 1:
                newline = f.readline()
                if newline == '':
                    f.close()                                                                                                              
                    break
                yield(newline.strip())

    if len(customlist) > 0:
        yield(customlist)                                                                                                    


    if defaults:
        # vertical numbers
        combinations = [['','147','258','369'],['','147*','2580','369#']]
        for verticalnumbers in combinations:
            for verticalnum1 in verticalnumbers:
                for verticalnum2 in verticalnumbers:
                    for verticalnum3 in verticalnumbers:
                        yield(''.join([verticalnum1,verticalnum2,verticalnum3]))
        
        for i in [012,123,234,345,456,567,678,789,890]:
            yield(str(i))

        for i in [1234,2345,3456,4567,5678,6789,7890,0123]:
            yield('%s' % i)

        for i in [12345,23456,34567,45678,56789,67890,01234]:
            yield('%s' % i)

        # give me 0101,0202, .. 2323 etc with different lengths.
        # guess repetitive numeric extensions
        for i in xrange(0,10):
            for j in xrange(0,10):
                for l in xrange(1,4):
                    yield(("%s%s" % (i,j)) * l)
                                              
        for i in xrange(1000,9999,100):
            yield('%04i' % i)


        for i in xrange(1001,9999,100):
            yield('%04i' % i)                                                                                                  

        for i in xrange(0,10):
            for l in xrange(1,8):
                yield(('%s' % i) * l)

        for i in xrange(0,1000,50):
            yield('%03i' % i)

        #for i in xrange(100,999):
            #yield('%s' % i)

        for i in xrange(10000,99999,100):
            yield('%04i' % i)

        for i in xrange(10001,99999,100):
            yield('%04i' % i)

        for i in xrange(10):
            yield('trunk_%s' % i)


def prefixgenerator(defaults=True,prefixranges=[],phonenumber='18778988646',paddinglength=4):
    if defaults:
        prefixranges.append([0,999])
    donelist = list()
    for prefixrange in prefixranges:
        startprefix = prefixrange[0]
        endprefix = prefixrange[1]
        for i in xrange(paddinglength):            
            for prefix in xrange(startprefix,endprefix):
                template = '%%0%si%%s' % i
                retnum = template % (prefix,phonenumber)
                if not retnum in donelist:
                    donelist.append(retnum)
                    yield(retnum)
                

def passwordgenerator(defaults=True,pwdrange=[],dictionary=None,customlist=[],extension=None,template=None):
    if len(pwdrange) > 0:
        for genrange in getRange(pwdrange):                                    
            if not template:
                template = '%i'
            for i in genrange:
                yield(template % i)

            

    if defaults:
        if extension is not None:
            # 21 iterations
            yield(str(extension))
    
            for i in xrange(10):
                yield(str(i)+str(extension))
    
            for i in xrange(10):
                yield(str(extension)+str(i))                                                                                                  

        combinations = [['','147','258','369'],['','147*','2580','369#']]
        for verticalnumbers in combinations:
            for verticalnum1 in verticalnumbers:
                for verticalnum2 in verticalnumbers:
                    for verticalnum3 in verticalnumbers:
                        yield(''.join([verticalnum1,verticalnum2,verticalnum3]))

        for i in [012,123,234,345,456,567,678,789,890]:
            yield(str(i))

        for i in [1234,2345,3456,4567,5678,6789,7890,0123]:
            yield(str(i))

        for i in [12345,23456,34567,45678,56789,67890,01234]:
            yield(str(i))
                                              
        for i in xrange(1900,datetime.now().year+1):
            yield(str(i))
        # give me 0101,0202, .. 2323 etc with different lengths
        for i in xrange(0,10):
            for j in xrange(0,10):
                for l in xrange(1,4):
                    yield(("%s%s" % (i,j)) * l)

        for i in xrange(0,10):
            for l in xrange(7,9):
                yield(('%s' % i) * l)                                                                                                            


        for i in xrange(1000,9999,100):
            yield('%04i' % i)


        for i in xrange(1001,9999,100):
            yield('%04i' % i)                                                                                                  

        for i in xrange(0,10):
            for l in xrange(1,8):
                yield(('%s' % i) * l)

        for i in xrange(0,1000,50):
            yield('%03i' % i)

        for i in xrange(100,999):
            yield('%s' % i)                                              

        for i in xrange(10000,99999,100):
            yield('%04i' % i)

        for i in xrange(10001,99999,100):
            yield('%04i' % i)

        for i in xrange(10):
            yield('trunk_%s' % i)

class anotherxrange(object):
    """A pure-python implementation of xrange.

    Can handle float/long start/stop/step arguments and slice indexing"""

    __slots__ = ['_slice']
    def __init__(self, *args):
        self._slice = slice(*args)
        if self._slice.stop is None:
            # slice(*args) will never put None in stop unless it was
            # given as None explicitly.
            raise TypeError("xrange stop must not be None")
        
    @property
    def start(self):
        if self._slice.start is not None:
            return self._slice.start
        return 0
    @property
    def stop(self):
        return self._slice.stop
    @property
    def step(self):
        if self._slice.step is not None:
            return self._slice.step
        return 1

    def __hash__(self):
        return hash(self._slice)

    def __cmp__(self, other):
        return (cmp(type(self), type(other)) or
                cmp(self._slice, other._slice))

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.start, self.stop, self.step)

    def __len__(self):
        return self._len()

    def _len(self):
        return max(0, int((self.stop - self.start) / self.step))

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._len())
            return xrange(self._index(start),
                          self._index(stop), step*self.step)
        elif isinstance(index, (int, long)):
            if index < 0:
                fixed_index = index + self._len()
            else:
                fixed_index = index
                
            if not 0 <= fixed_index < self._len():
                raise IndexError("Index %d out of %r" % (index, self))
            
            return self._index(fixed_index)
        else:
            raise TypeError("xrange indices must be slices or integers")

    def _index(self, i):
        return self.start + self.step * i    
