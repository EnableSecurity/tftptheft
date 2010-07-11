#!/usr/bin/env python

import progressbar
from time import sleep
widgets = ["W"]
bar = progressbar.ProgressBar()
bar.start()
for i in xrange(100):
    bar.update(bar.currval+1)
    sleep(0.1)
bar.finish()