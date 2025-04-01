# python3 resize.py /path/to/original/images/

import os
from os import listdir
from os.path import isfile, join
import sys

from PIL import Image

inpath = sys.argv[1]

onlyfiles = [f for f in listdir(inpath) if isfile(join(inpath, f)) and f.endswith(".jpg")]
outfiles = []

size = (300, 300)
for image in onlyfiles:
    outfile = inpath + image.replace('.jpg', '_300.jpg')
    outfiles.append(outfile)
    infile = inpath + image
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                im.thumbnail(size)
                im.save(outfile, "JPEG")
        except OSError:
            print("cannot create thumbnail for", infile)

for o in outfiles:
    im = Image.open(o)
    print(im.format, im.size, im.mode)
    im.show()
