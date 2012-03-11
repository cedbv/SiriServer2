#!/usr/bin/python
# -*- coding: utf-8 -*-
# Horoscope
# Par Cédric Boverie (cedbv)

import re
import xml.etree.ElementTree as ET
import urllib, urllib2
from plugin import *


class horoscopeFr(Plugin):
    @register("fr-FR", ".*horoscope.*")
    def horoscope(self, speech, language):

        speech = speech.lower()

        if speech.count(u"bélier"):
            signe = u"Bélier"
            signe_id = 0
        elif speech.count("taureau"):
            signe = u"Taureau"
            signe_id = 1
        elif speech.count(u"gémeaux"):
            signe = u"Gémeaux"
            signe_id = 2
        elif speech.count("cancer"):
            signe = u"Cancer"
            signe_id = 3
        elif speech.count("lion"):
            signe = u"Lion"
            signe_id = 4
        elif speech.count("vierge"):
            signe = u"Vierge"
            signe_id = 5
        elif speech.count("balance"):
            signe = u"Balance"
            signe_id = 6
        elif speech.count("scorpion"):
            signe = u"Scorpion"
            signe_id = 7
        elif speech.count("sagittaire"):
            signe = u"Sagittaire"
            signe_id = 8
        elif speech.count("capricorne"):
            signe = u"Capricorne"
            signe_id = 9
        elif speech.count("verseau"):
            signe = u"Verseau"
            signe_id = 10
        elif speech.count("poisson") or speech.count("poissons"):
            signe = u"Poissons"
            signe_id = 11
        else:
            self.say(u"Je n'arrive pas à trouver votre signe.")
            self.complete_request()
            return

        self.say(u"Je recherche l'horoscope pour {0}...".format(signe))

        horoscope = None
        try:
            response = urllib2.urlopen("http://www.astrocenter.fr/fr/feeds/rss-horoscope-jour-signe.aspx?sign={0}".format(signe_id), timeout=5).read()
            xml = ET.fromstring(response)
            horoscope = xml.find("channel/item/description").text
            horoscope = re.sub('<br/>(.*)', '', horoscope)
        except:
            pass

        if horoscope != None:
            self.say(horoscope)
        else:
            self.say(u"Il y a eu une erreur lors de la récupération de votre horoscope.")

        self.complete_request()