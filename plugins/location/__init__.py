#!/usr/bin/python
# -*- coding: utf-8 -*-

# Based on the WhereAmI plugins

import re
import urllib2, urllib
import json
import math
from plugin import *

from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.systemObjects import GetRequestOrigin,Location
from siriObjects.localsearchObjects import Business, MapItem, MapItemSnippet, Rating

APIKEY = APIKeyForAPI("googleplaces")

try:
    TOMTOM_APIKEY = APIKeyForAPI("tomtom")
except:
    TOMTOM_APIKEY = ""
# Get an API Key here:
# http://www.tomtom.com/addto/one-address-wizard.php
# (Check in the generated html code)

class location(Plugin):

    res = {
        'results_found': {
            'fr-FR': u"J'ai trouvé {0} résultats : ",
            'en-US': u"I found {0} results : ",
            },
        'no_result': {
            'fr-FR': u"Pas de résultat.",
            'en-US': u"No result.",
            },
        'no_location_found': {
            'fr-FR': u"Désolé, je n'arrive pas à trouver cet endroit !",
            'en-US': u"No location found!",
            'de-DE': u"Ich habe keinen Ort gefunden!",
            },
        'connection_error': {
            'fr-FR': u"Il m'est impossible de contacter Google pour le moment ! Veuillez réessayer plus tard.",
            'en-US': u"Il m'est impossible de contacter Google pour le moment ! Veuillez réessayer plus tard.",
            'de-DE': u"Ich konnte keine Verbindung zu Googlemaps aufbauen",
            },
        'you_are': {
            'fr-FR': u"Vous êtes {0}.",
            'en-US': u"You are {0}.",
            },
        'google_useless': {
            'fr-FR': u"Les informations demandées ne sont pas sur Google Maps !",
            'en-US': u"The Googlemaps response did not hold the information i need!",
            'de-DE': u"Die Googlemaps informationen waren ungenügend!",
            },
        'here_is': {
            'fr-FR': u"Voici l'emplacement de {0} :\n{1}",
            'en-US': u"Here is {0}:\n{1}",
            'de-DE': u"Hier liegt {0}:\n{1}",
            },
        }


    @register("fr-FR", u".*o(ù|u) puis.je trouv(é|e)r? (?P<keyword>.*)( par ici| paris 6| près (d'ici|de moi)| (la|les?) plus proches?| dans les environs?| (a|à) proximit(é|e)| dans le coin)?.*|.*(trouv(e|ait|ais)|cherch(e|é)r?|est|sont) (?P<keyword2>.*) (par ici|paris 6|près d'ici|près de moi|(la|les?) plus proches?|dans les environs?|(a|à) proximit(é|e)|dans le coin).*")
    @register("en-US",".*(where|find|show).* (nearest|nearby|closest) (?P<keyword>.*)")
    def whereisPlaces(self, speech, language, regex):
        res = self.res
        keyword = regex.group('keyword')
        if keyword == None:
            keyword = regex.group('keyword2')
        keyword = keyword.strip();

        if language == 'fr-FR':
            keyword = keyword.replace(u"près ","").replace(u"plus proches","").replace(u"plus proche","").replace(u"à proximité","").replace(u"dans le coin","").replace(u"coin ","").replace("par ","").replace('la ','').replace('les ','').replace('le ','').replace('des ','').replace('de ','').replace('du ','').replace('une ','').replace('un ','').replace("dans ","")
        elif language == 'en-US':
            keyword = keyword.replace(u"near by ","").replace(u"nearby ","").replace(u"the ","").replace(u"an ","").replace(u"a ","")

        location = self.getCurrentLocation(force_reload=True,accuracy=GetRequestOrigin.desiredAccuracyBest)
        latlong = str(location.latitude)+","+str(location.longitude)

        if language == "fr-FR" and speech.count("pied") > 0:
            radius = "2500"
            keyword = keyword.replace(u"à pied","").replace(u"a pied","").replace("pied","")
        elif language == "en-US" and speech.count("walk") > 0:
            radius = "2500"
            keyword = keyword.replace(u"in walking distance","").replace(u"walking distance","").replace(u"walking","").replace("walk","")
        else:
            radius = "15000"

        print "Keyword : " + keyword

        response = None
        url = "https://maps.googleapis.com/maps/api/place/search/json?location={0}&radius={1}&keyword={2}&sensor=true&key={3}".format(latlong,radius,urllib.quote_plus(keyword.encode("utf-8")),APIKEY)
        print url
        try:
            jsonString = urllib2.urlopen(url, timeout=3)
            response = json.load(jsonString);
        except:
            pass

        if response["status"] == "OK":

            results = []
            for result in response["results"]:
                ident = result["id"]
                name = result["name"]
                lat = result["geometry"]["location"]["lat"]
                lng = result["geometry"]["location"]["lng"]
                vicinity = result["vicinity"]
                if "rating" in result:
                    rate = result["rating"]
                    nb_review = 1
                else:
                    rate = 0.0
                    nb_review = 0

                #distance = self.haversine_distance(location.latitude, location.longitude, lat, lng)

                rating = Rating(value=rate, providerId='Google', count=nb_review)
                details = Business(totalNumberOfReviews=nb_review,name=name,rating=rating)

                mapitem = MapItem(label=name, street="", stateCode="", postalCode="",latitude=lat, longitude=lng)
                mapitem.detail = details
                results.append(mapitem)

            mapsnippet = MapItemSnippet(items=results)
            view = AddViews(self.refId, dialogPhase="Completion")
            view.views = [AssistantUtteranceView(speakableText=res["results_found"][language].format(len(response["results"])), dialogIdentifier="googlePlacesMap"), mapsnippet]
            self.sendRequestWithoutAnswer(view)

        elif response["status"] == "ZERO_RESULTS":
            self.say(res["no_result"][language])
        else:
            self.say(res["connection_error"][language])
        self.complete_request()

    @register("de-DE", "(Wo bin ich.*)")
    @register("en-US", "(Where am I.*)")
    @register("fr-FR", u"((ou|où).*suis.*je.*)")
    def whereAmI(self, speech, language):
        location = self.getCurrentLocation(force_reload=True,accuracy=GetRequestOrigin.desiredAccuracyBest)
        url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&sensor=false&language={2}".format(str(location.latitude),str(location.longitude), language)
        jsonString = None
        city = ""
        country = ""
        state = ""
        stateLong = ""
        countryCode = ""
        result = ""
        street = ""
        postal_code = ""
        try:
	        jsonString = urllib2.urlopen(url, timeout=3).read()
	        response = json.loads(jsonString)
	        components = response['results'][0]['address_components']
	        result = response['results'][0]['formatted_address'];
        except:
	        pass
        if components != None:
            city = filter(lambda x: True if "locality" in x['types'] or "administrative_area_level_1" in x['types'] else False, components)[0]['long_name']
            country = filter(lambda x: True if "country" in x['types'] else False, components)[0]['long_name']
            state = filter(lambda x: True if "administrative_area_level_1" in x['types'] or "country" in x['types'] else False, components)[0]['short_name']
            stateLong = filter(lambda x: True if "administrative_area_level_1" in x['types'] or "country" in x['types'] else False, components)[0]['long_name']
            countryCode = filter(lambda x: True if "country" in x['types'] else False, components)[0]['short_name']
            street = filter(lambda x: True if "route" in x['types'] else False, components)[0]['short_name']
            street_number = filter(lambda x: True if "street_number" in x['types'] else False, components)[0]['short_name']
            street = street + " " + street_number
            postal_code = filter(lambda x: True if "postal_code" in x['types'] else False, components)[0]['short_name']

        view = AddViews(self.refId, dialogPhase="Completion")
        text_to_speak = self.res["you_are"][language].format(result)
        mapsnippet = MapItemSnippet(items=[MapItem(label=postal_code+" "+city, street=street, city=city, postalCode=postal_code, latitude=location.latitude, longitude=location.longitude, detailType="CURRENT_LOCATION")])
        view.views = [AssistantUtteranceView(speakableText=text_to_speak, dialogIdentifier="Map#whereAmI"), mapsnippet]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()

    @register("de-DE", "(Wo liegt.*)")
    @register("en-US", "(Where is.*)")
    @register("fr-FR", u"(ouai|.*o(ù|u)) (est |se trouve |ce trouve |se situe |ce situe )(.*)")
    def whereIs(self, speech, language, regex):
        the_location = None
        if language == "de-DE":
            the_location = re.match("(?u).* liegt ([\w ]+)$", speech, re.IGNORECASE)
            the_location = the_location.group(1).strip()
        elif language == 'fr-FR':
            the_location = regex.group(regex.lastindex).strip()
        else:
            the_location = re.match("(?u).* is ([\w ]+)$", speech, re.IGNORECASE)
            the_location = the_location.group(1).strip()

        print the_location
        if the_location != None:
            the_location = the_location[0].upper()+the_location[1:]
        else:
            self.say(self.res["no_location_found"][language])
            self.complete_request()
            return
        url = u"http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false&language={1}".format(urllib.quote_plus(the_location.encode("utf-8")), language)
        jsonString=None
        try:
            jsonString = urllib2.urlopen(url, timeout=3).read()
        except:
            pass
        if jsonString != None:
            response = json.loads(jsonString)
            if response['status'] == 'OK':
                location = response['results'][0]['geometry']['location']
                city=response['results'][0]['address_components'][0]['long_name']
                try:
                    emplacement = response['results'][0]["formatted_address"]
                    country=response['results'][0]['address_components'][2]['long_name']
                    countryCode=response['results'][0]['address_components'][2]['short_name']
                except:
                    emplacement=the_location
                    country=the_location
                    countryCode=the_location

                the_header = self.res["here_is"][language].format(the_location, emplacement)

                view = AddViews(self.refId, dialogPhase="Completion")
                mapsnippet = MapItemSnippet(items=[MapItem(label=city, latitude=str(location['lat']),longitude=str(location['lng']), detailType="ADDRESS_ITEM")])
                view.views = [AssistantUtteranceView(speakableText=the_header, dialogIdentifier="Map"), mapsnippet]
                self.sendRequestWithoutAnswer(view)

                if TOMTOM_APIKEY != "":
                    if language == "fr-FR":
                        button_txt = u"Ouvrir dans TomTom"
                    else:
                        button_txt = "Open in TomTom"

                    url = u"http://addto.tomtom.com/api/home/v2/georeference?action=add&apikey={0}&latitude={1}&longitude={2}&name={3}".format(TOMTOM_APIKEY, str(location['lat']), str(location['lng']), urllib.quote_plus(the_header.encode("utf-8")))
                    button = Button(text=button_txt, commands=[OpenLink(ref=url.replace('//',''))])
                    self.send_object(AddViews(self.refId, views=[button]))

            else:
                self.say(self.res["google_useless"][language])
        else:
            self.say(self.res["connection_error"][language])
        self.complete_request()

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        RAD_PER_DEG = 0.017453293
        Rkm = 6371
        dlon = lon2-lon1
        dlat = lat2-lat1
        dlon_rad = dlon*RAD_PER_DEG
        dlat_rad = dlat*RAD_PER_DEG
        lat1_rad = lat1*RAD_PER_DEG
        lon1_rad = lon1*RAD_PER_DEG
        lat2_rad = lat2*RAD_PER_DEG
        lon2_rad = lon2*RAD_PER_DEG

        a = (math.sin(dlat_rad/2))**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * (math.sin(dlon_rad/2))**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return round(Rkm * c,2)
