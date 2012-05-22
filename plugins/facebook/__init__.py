#!/usr/bin/python
# -*- coding: utf-8 -*-
# Post to Facebook
# Par Cédric Boverie (cedbv)

# This plugin requires a web server (like Apache) with SiriServer-WebAddons (a php script) installed.
# https://github.com/cedbv/SiriServer-WebAddons
# TODO: Use a db instead of facebook.conf
# TODO: documentation

import re
from plugin import *
import ConfigParser
import urllib, urllib2

configFile = APIKeyForAPI("webaddons_path")+"/facebook.conf"
webaddons_url = APIKeyForAPI("webaddons_url")

class Facebook(Plugin):

    res = {
        'facebook': {
            'en-US': u".*(facebook)(.*)",
            'fr-FR': u".*(facebook)(.*)",
        },
        'what_to_post': {
            'en-US': u"What do you want to post to Facebook?",
            'fr-FR': u"Que voulez-vous envoyer sur Facebook ?",
        },
        'success': {
            'en-US': u"I just posted \"{0}\" on Facebook.",
            'fr-FR': u"J'ai envoyé \"{0}\" sur Facebook.",
        },
        'failure': {
            'en-US': u"Something doesn't work as expected. Try again later.",
            'fr-FR': u"Quelque chose s'est mal passé. Veuillez réessayer plus tard.",
        },
        'not_ready': {
            'en-US': u"Your Facebook account is not configured. Connect with the following button :",
            'fr-FR': u"Votre compte Facebook n'est pas configuré. Vous pouvez vous connecter avec ce bouton :",
        },
    }

    @register("fr-FR", res["facebook"]["fr-FR"])
    @register("en-US", res["facebook"]["en-US"])
    def post(self, speech, language, regex):

        if regex.group(2) != None:
            msg = regex.group(2).strip()
        else:
            msg = ""

        config = ConfigParser.RawConfigParser()
        config.read(configFile)
        try:
            access_token = config.get(self.assistant.accountIdentifier,"access_token")
        except:
            access_token = ""

        if access_token != "":
            if msg == "":
                msg = self. ask(self.res["what_to_post"][language])
            try:
                url = 'https://graph.facebook.com/me/feed'
                data = urllib.urlencode({'access_token' : access_token,'message' : msg})
                req = urllib2.Request(url, data)
                response = urllib2.urlopen(req).read()
                self.say(self.res["success"][language].format(msg))
            except:
                self.say(self.res["failure"][language])
        else:
            self.say(self.res["not_ready"][language])
            url = webaddons_url+"/facebook.php?id=" + self.assistant.accountIdentifier

            view = UIAddViews(self.refId)
            button = UIButton()
            button.text = u"Connectez-vous sur Facebook"
            link = UIOpenLink("")
            link.ref = url.replace("//","")
            button.commands = [link]
            view.views = [button]
            self.send_object(view)
            
        self.complete_request()
