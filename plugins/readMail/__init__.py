#!/usr/bin/python
# -*- coding: utf-8 -*-
#Made by Maxx
#Thanks to JimmyKane and his debug level 9 for the siriproxy (<333) and Eichhoernchen for
#making the python siriserver
#Credits to gaVRos for some minor adjustments and testing

import re
import logging
import time
import pytz

from datetime import *
from pytz import timezone
from uuid import uuid4
from plugin import *

from siriObjects.baseObjects import *
from siriObjects.uiObjects import *
from siriObjects.systemObjects import *
from siriObjects.emailObjects import *

checkEmail_tr = {
                    "letmecheck" : {
                        "en-US" : "Let me check your mail...",
                        "fr-FR" : u"Je vérifie vos derniers mails...",
                    },
                    "donthave" : {
                        "en-US" : "Looks like you don't have any email.",
                        "fr-FR" : u"Vous n'avez apparement aucun message.",
                    },
                    "found" : {
                        "en-US" : "Ok, here is what I found: ",
                        "fr-FR" : u"Ok, voilà ce que j'ai trouvé :",
                    },
                    "noaccount" : {
                        "en-US" : "You don't have an email account set up yet.",
                        "fr-FR" : u"Vous n'avez pas encore de compte mail enregistré.",
                    },
                    "openmailapp" : {
                        "en-US" : "Just launch the Mail app, it will guide you through the setup process.",
                        "fr-FR" : u"Lancer simplmement l'application Mail. Elle vous guidera durant le paramétrage de votre compte.",
                    },
                }

class checkEmail(Plugin):

    #Command to activate the checking of email...
    @register("en-US","(.*check.* (.*mail.*)|(.*email.*))")
    @register("en-GB","(.*check.* (.*mail.*)|(.*email.*))")
    @register("fr-FR",".*mail.*")
    def emailSearch(self, speech, language):

        #Let user know siri is searching for your mail GOOD!
        view_initial = AddViews(self.refId, dialogPhase="Reflection")
        view_initial.views = [AssistantUtteranceView(speakableText=checkEmail_tr["letmecheck"][language], dialogIdentifier="EmailFindDucs#findingNewEmail")]
        self.sendRequestWithoutAnswer(view_initial)

        #Grabs the timeZone given by the client
        tz = timezone(self.connection.assistant.timeZoneId)

        #Search object to find the mail GOOD!
        email_search = EmailSearch(self.refId)
        email_search.timeZoneId = self.connection.assistant.timeZoneId
        email_search.startDate = datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=tz)
        email_search.endDate = datetime.now(tz)
        email_return = self.getResponseForRequest(email_search)

        if email_return["class"] != "CommandFailed":
            if email_return["properties"]["emailResults"] == []:
                view = AddViews(self.refId, dialogPhase="Summary")
                view.views += [AssistantUtteranceView(speakableText=checkEmail_tr["donthave"][language], dialogIdentifier="EmailFindDucs#foundNoEmail")]
                self.sendRequestWithoutAnswer(view)
            else:
                email_ = email_return["properties"]["emailResults"]
                #Display the mail! It works :D!
                view = AddViews(self.refId, dialogPhase="Summary")
                view1 = AssistantUtteranceView(speakableText=checkEmail_tr["found"][language], dialogIdentifier="EmailFindDucs#foundEmail")
                snippet = EmailSnippet()
                snippet.emails = email_
                view2 = snippet
                view.views = [view1, view2]
                self.sendRequestWithoutAnswer(view)
        else:
            view = AddViews(self.refId, dialogPhase="Summary")
            view1 = AssistantUtteranceView(speakableText=checkEmail_tr["noaccount"][language], dialogIdentifier="EmailCreateDucs#noEmailAccount")
            view2 = AssistantUtteranceView(speakableText=checkEmail_tr["openmailapp"][language], dialogIdentifier="EmailCreateDucs#noEmailAccount")
            view.views = [view1, view2]
            self.sendRequestWithoutAnswer(view)
        self.complete_request()