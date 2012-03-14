#!/usr/bin/python
# -*- coding: utf-8 -*-

# Random VDM or FML
# Use iPhone App API
# By Cédric Boverie (cedbv)

import re
import xml.etree.ElementTree as ET
import urllib2, urllib
import random
from plugin import *


class vieDeMerde(Plugin):

    @register("fr-FR", ".*vie.*(merde|merd).*|.*vdm.*")
    @register("en-US", ".*fuck.*my.*(life|live).*|.*fml.*")
    def fuckMyLife(self, speech, language):
        vdm = None
        lang = language[:2]
        try:
            response = urllib2.urlopen("http://www.vdm-iphone.com/v8/{0}/random.php?cat=all&num_page=0".format(lang), timeout=5).read()
            xml = ET.fromstring(response)
            vdms = xml.findall("item")
            vdm = random.choice(vdms)
        except:
            pass

        if vdm != None:
            self.say(vdm.find("text").text)
            url = vdm.find("short_url").text.replace("//","")

            if language == "fr-FR":
                button_txt = "Lire sur VDM"
            else:
                button_txt = "Read on FML"

            button = Button(text=button_txt, commands=[OpenLink(ref=url)])
            self.send_object(AddViews(self.refId, views=[button]))
        else:
            if language == "fr-FR":
                self.say(u"Désolé, aujourd'hui est une journée tellement merdique que je n'arrive même pas à lire VDM.")
            else:
                self.say("I can't read FMyLife. FML")

        self.complete_request()
