#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import os
import sys
import zlib

import Image
import qrencode

DIVIDE = 768
MAXWIDTH = 1000
SCALERATIO = 2

if len(sys.argv) < 2:
    print "Usage: python file2qr.py <filepath>"
    exit()

src = sys.argv[1]

if not os.path.isfile(src):
    print "Invalid file."
    exit()

x = os.popen('zbarimg %s' % src)
lines = x.readlines()

groups = {}
for each in lines:
    if not each.startswith('QR-Code:'):
        continue
    each = each[8:]
    adler32 = each[0:6]
    seqid = int('0x' + each[6:8],16)
    if not groups.has_key(adler32):
        groups[adler32] = {}
    eachdata = each[8:] + '=' * (len(each) % 4)
    groups[adler32][seqid] = eachdata.decode('base64')

for adler32 in groups:
    dataset = groups[adler32]
    gotkeys = dataset.keys().sort()
    if not gotkeys:
        continue
    if max(gotkeys) != len(gotkeys) - 1:
        print "Not all QR-Codes scanned in for file [%s]. More data needed." % adler32
