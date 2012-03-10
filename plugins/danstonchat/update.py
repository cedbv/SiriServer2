#!/usr/bin/python
# -*- coding: utf-8 -*-
# Update fortunes file from danstonchat.com(http://danstonchat.com/fortunes)
# Par Cédric Boverie (cedbv)

import os
import urllib, urllib2

urlfile = urllib2.urlopen("http://danstonchat.com/fortunes")
fichier = os.path.dirname(os.path.abspath(__file__))+"/fortunes"
fichier_temp = os.path.dirname(os.path.abspath(__file__))+"/fortunes2"

print "Downloading Danstonchat.com's fortunes..."
f = open(fichier_temp, "wb")
for line in urlfile:
    f.write(line)
f.close()
urlfile.close()
print "Download OK."

try:
    os.remove(fichier)
except:
    pass
os.rename(fichier_temp, fichier)

print "Update OK."