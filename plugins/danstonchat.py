#!/usr/bin/python
# -*- coding: utf-8 -*-
# Quote au hasard de danstonchat.com
# Emplacement du fichier fortunes : http://danstonchat.com/fortunes
# Par Cédric Boverie (cedbv)

import os
import re
import random
from plugin import *

class dansTonChat(Plugin):

    fichier = open(os.path.dirname(__file__)+"/danstonchat-fortunes","r")
    fortunes = ""
    for ligne in fichier:
        fortunes += ligne
    fichier.close()
    fortunes = fortunes.split("%")

    @register("fr-FR", ".*dans.*ton.*chat.*")
    def dtc(self, speech, language):

        fortune = random.choice(self.fortunes).decode("utf-8")
        try:
            url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', fortune)[0]
            fortune = fortune.replace("\n-- "+url,"").strip()
        except:
            pass

        self.say(fortune)
        if url != None:
            url = url.replace("//","")
            button = Button(text=u"Lire sur DansTonChat", commands=[OpenLink(ref=url)])
            self.send_object(AddViews(self.refId, views=[button]))

        self.complete_request()
