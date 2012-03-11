#!/usr/bin/python
# -*- coding: utf-8 -*-
# Annuaire téléphonique
# Annuaire téléphonique avec l'API de truvo.net
# Par Cédric Boverie (cedbv)

import re
import xml.etree.ElementTree as ET
import urllib2, urllib

from plugin import *

class Annuaire(Plugin):
        
    @register("fr-FR", u".*recherche (.*) dans l'annuaire.*|.*(annuaire) ?(.*)")
    def white(self, speech, language, regex):
        
        search = regex.group(regex.lastindex).strip()
        
        city = re.match(u"(.*) (a|à|de|pour|dans|en|in) (.*)", search, re.IGNORECASE)
        if city != None:
            search = city.group(1).strip()
            city = city.group(city.lastindex).strip()
        else:
            city = "belgium"
        
        try:
            location = self.getCurrentLocation(force_reload=True,accuracy=GetRequestOrigin.desiredAccuracyBest)
            url = "http://mobileproxy.truvo.net/BE/white/search.ds?platform=ipad&version=3&locale=fr_BE&what={0}&where={1}&distLatitude={2}&distLongitude={3}&activeSort=geo_spec_sortable".format(urllib.quote_plus(search.encode("utf-8")), urllib.quote_plus(city.encode("utf-8")), location.latitude, location.longitude)
            print url
            response = urllib2.urlopen(url, timeout=5).read()
            xml = ET.fromstring(response)
        except:
            self.say(u"Il m'est impossible d'accéder à l'annuaire pour le moment !")
            self.complete_request()
            return
            
        empty = True
        for listing in xml.find("listings"):
            if listing.get("type") != 'ad':
                empty = False
                fiche = listing.find("businessName").text + "\n"
                #print listing.find("distance").text
                fiche += listing.find("streetAddress").text + "\n"
                fiche += listing.find("zipCode").text + " " + listing.find("city").text + "\n"
                if listing.find("phoneNumbers").find("number") != None:
                    fiche += listing.find("phoneNumbers").find("number").text.replace(' ','/')
                self.say(fiche, fiche.replace("\n",",\n").replace(".-","-"))

        if empty:
            self.say(u"Aucun résultat pour {0}.".format(search))

        
        self.complete_request()     
