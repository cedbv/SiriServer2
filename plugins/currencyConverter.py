#!/usr/bin/python
# -*- coding: utf-8 -*-
# Convertisseur de monnaie
# Par Cédric Boverie (cedbv)

import re
import urllib2, urllib
from plugin import *

class currencyConverter(Plugin):

    def str2CurrencyCode(self, string):
        if string == "euros" or string == "euro":
            return "EUR"
        elif string == "dollar" or string == "dollars":
            return "USD"
        else:
            return ""

    @register("fr-FR", ".*(chang(e|é)r?|converti(s|t|r)?|convertisseur) (?P<amount>[0-9,\.]+) (?P<from>[^ ]+) en (?P<to>[^ ]+)")
    def converter(self, speech, language, regMatched):

        amount = regMatched.group("amount").strip()
        currency_from = regMatched.group("from").strip()
        currency_to = regMatched.group("to").strip()

        currency_from_code = self.str2CurrencyCode(currency_from)
        currency_to_code = self.str2CurrencyCode(currency_to)

        if currency_from_code == currency_to_code:
            self.say(u"Voyons, vous savez faire ce calcul vous même...")
            self.complete_request()
            return
        elif currency_from_code == "" or currency_to_code == "":
            self.say(u"Je n'ai pas trouvé toutes les monnaies nécessaires...")
            self.complete_request()
            return

        try:
            amount = amount.replace(",",".").replace(" ","")
            amount = float(amount)
        except:
            self.say(u"Je n'arrive pas à interpréter la valeur recherchée.")
            self.complete_request()
            return


        self.say(u"Je recherche combien font "+str(amount)+" "+currency_from+" en "+currency_to+"...")

        change = None
        try:
            change = urllib2.urlopen("http://quote.yahoo.com/d/quotes.csv?s={0}{1}=X&f=l1&e=.csv".format(currency_from_code,currency_to_code), timeout=5).read()
        except:
            pass

        if change != None:
            self.say(str(amount) + " " + currency_from + u" équivaut à " +str(round(amount*float(change),2))+ " "+currency_to + ".")
        else:
            self.say(u"Je n'arrive pas à obtenir le taux de change actuel.")

        self.complete_request()