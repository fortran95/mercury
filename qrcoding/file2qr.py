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

srccontent = open(src,'r').read()
compressed = zlib.compress(srccontent)
usecompress = False
if len(compressed) < len(srccontent):
    usecompress = True
    srccontent = compressed

controlbyte = chr(usecompress << 0)
adler32 = hex(abs(zlib.adler32(srccontent)))[2:].decode('hex').encode('base64').replace('\n','').rstrip('=')

srccontent = controlbyte + srccontent
parts = []
while srccontent:
    parts.append(srccontent[0:DIVIDE])
    srccontent = srccontent[DIVIDE:]

# ## ###

qrimages = []
maxsize = 0

seqid = 0
for each in parts:
    packaged = adler32 + hex(seqid)[2:].zfill(2) + \
               each.encode('base64').replace('\n','').rstrip('=')
    qrc = qrencode.encode(packaged,
                          0,
                          qrencode.QR_ECLEVEL_M,
                          qrencode.QR_MODE_KANJI,
                          True)
    qrimages.append((qrc[1],qrc[2]))
    maxsize = max(maxsize,qrc[1])
    seqid += 1

# Joining all small codes
imagescount = len(qrimages)
maxsize = int(maxsize * 1.2)

colmax = max(1,
             min(math.sqrt( imagescount ),math.floor(MAXWIDTH * 1.0 / maxsize / SCALERATIO )))
rowmax = math.ceil(imagescount * 1.0 / colmax)
margin = int(0.1 * maxsize)

product = Image.new('L',(maxsize * colmax, maxsize * rowmax),255)

rowid, colid = 1, 1

for qrsize, qrimg in qrimages:
    product.paste(qrimg,( margin + (colid - 1) * maxsize, margin + (rowid - 1) * maxsize))
    colid += 1
    if colid > colmax:
        colid = 1
        rowid += 1

print "Generated %d pieces, spread in %d x %d." % (imagescount, rowmax, colmax)

product.save('product.gif','GIF')
product.show()

product.save('product.png','PNG')

largeproduct = product.resize((product.size[0] * SCALERATIO, product.size[1] * SCALERATIO))
largeproduct.save('product.large.jpg','JPEG')
largeproduct.save('product.large.png','PNG')
