#!/usr/bin/python
# -*- coding: utf-8 -*-
# Programme TV
# Utilise l'API de l'application iPhone de Moustique.be
# Par Cédric Boverie (cedbv)

import re
import xml.etree.ElementTree as ET
import urllib2, urllib
from datetime import datetime,timedelta
import time

from plugin import *

class tvBelgium(Plugin):
        
    @register("fr-FR", u".*(tv|t(é|e)l(é|e)vision|t(é|e)l(é|e) | t(é|e)l(é|e)).*")
    def moustique(self, speech, language, regex):
        try:
            response = urllib2.urlopen("http://api.moustique.be/pota/epg/getbroadcasterlist/data.xml", timeout=30).read()
            xml = ET.fromstring(response)
            chaines = {}
            for broadcast in xml:
                chaines[broadcast.get("id")] = broadcast.find("display_name").text
        except:
            self.say(U"Une erreur est survenue pendant la récupération des chaînes.")
            self.complete_request()
            return
            
        today = datetime.today()

        # Soiréee
        soiree = False
        soiree_debut_timestamp = None
        soiree_fin_timestamp = None
        if speech.count("soir") > 0:
            soiree = True
            soiree_debut_timestamp = time.mktime(today.replace(hour=20,minute=0,second=0).timetuple())
            soiree_fin_timestamp = time.mktime(today.replace(hour=22,minute=0,second=0).timetuple())

        # Programme de la veille jusqu'à 5h30
        if soiree == False and today.hour <= 5 and today.minute < 30:
            today = today-timedelta(days=1)
            
        today_string = today.strftime(u"%Y-%m-%d")
        
        try:
            response = urllib2.urlopen("http://api.moustique.be/pota/epg/getprograms/{0}/data.xml".format(today_string), timeout=30).read()
            xml = ET.fromstring(response)
        except:
            self.say(u"Désolé, les piles de la télécommande sont plates. Veuillez réessayer plus tard.")
            self.complete_request()
            return

        currenttime = time.time()
        for broadcaster in xml:
            nom_chaine = chaines[broadcaster.get("id")]
            for program in broadcaster:
                title = program.find("title").text
                starttime_time = time.strptime(program.find("starttime").text, "%Y-%m-%d %H:%M:%S")
                endtime_time = time.strptime(program.find("endtime").text, "%Y-%m-%d %H:%M:%S")
                starttime_timestamp = time.mktime(starttime_time)
                endtime_timestamp = time.mktime(endtime_time)
                
                afficher = False
                
                if soiree == True and starttime_timestamp > soiree_debut_timestamp and starttime_timestamp < soiree_fin_timestamp:
                    afficher = True
                # Programmes en cours ou qui commence dans moins de 30 minutes, et non-terminés
                elif soiree == False and starttime_timestamp < currenttime+1800 and endtime_timestamp > currenttime:
                    afficher = True
                
                if afficher == True:
                    self.say(u"{0} sur {1} de {2} à {3}.".format(title,nom_chaine, time.strftime(u"%H:%M", starttime_time), time.strftime(u"%H:%M", endtime_time)))

        self.complete_request()     
