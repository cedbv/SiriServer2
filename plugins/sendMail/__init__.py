#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------
Authors :
Created by Daniel Zaťovič (P4r4doX)
Contacts search code is taken from phonecalls plugin by Eichhoernchen
Special thanks to doratown for providing original plists from 4S
---------------------------------------------------------------------
About :
Using this plugin you can write email directly from Siri
---------------------------------------------------------------------
Usage :
Email <name> about <subject>
---------------------------------------------------------------------
Todo :
Check email
---------------------------------------------------------------------
Instalation :
Just create folder called email in your plugins directory, and place
this file into it. Then add "mail" to your plugins.conf
---------------------------------------------------------------------
IMPORTANT :
You MUST download the newest version of SiriServerCore. becouse
Eichhoernchen have changed some objects to work with this plugin.
---------------------------------------------------------------------
Changelog :
v1.0 (19th March 2012) - initial Alpha release
"""


from plugin import *
from siriObjects.baseObjects import *
from siriObjects.uiObjects import *
from siriObjects.emailObjects import *
from siriObjects.systemObjects import *
from siriObjects.contactObjects import PersonSearch, PersonSearchCompleted
from plugin import *
from siriObjects.phoneObjects import PhoneCall
import re
import time

responses = {
'notFound':
    {'de-DE': u"Entschuldigung, ich konnte niemanden in deinem Telefonbuch finden der so heißt",
     'en-US': u"Sorry, I did not find a match in your phone book",
     'fr-FR': u"Désolé, je n'ai trouvé aucune correspondance dans votre carnet d'adresse."
    },
'devel':
    {'de-DE': u"Entschuldigung, aber diese Funktion befindet sich noch in der Entwicklungsphase",
     'en-US': u"Sorry this feature is still under development",
     'fr-FR': u"Désolé, cette fonctionnalité est encore en cours de développement."
    },
'select':
    {'de-DE': u"Wen genau?",
     'en-US': u"Which one?",
     'fr-FR': u"Lequel ?"
    },
'selectNumber':
    {'de-DE': u"Welche Email Adresse für {0}",
     'en-US': u"Which email adress one for {0}",
     'fr-FR': u"Quelle adresse email pour {0}"
    }
}

numberTypesLocalized= {
'_$!<Mobile>!$_': {'en-US': u"mobile", 'de-DE': u"Handynummer", 'fr-FR': u"mobile"},
'iPhone': {'en-US': u"iPhone", 'de-DE': u"iPhone-Nummer", 'fr-FR': u"iPhone"},
'_$!<Home>!$_': {'en-US': u"home", 'de-DE': u"Privatnummer", 'fr-FR': u"domicile"},
'_$!<Work>!$_': {'en-US': u"work", 'de-DE': u"Geschäftsnummer", 'fr-FR': u"bureau"},
'_$!<Main>!$_': {'en-US': u"main", 'de-DE': u"Hauptnummer",'fr-FR': u"principal"},
'_$!<HomeFAX>!$_': {'en-US': u"home fax", 'de-DE': u'private Faxnummer', 'fr-FR': u'fax domicile'},
'_$!<WorkFAX>!$_': {'en-US': u"work fax", 'de-DE': u"geschäftliche Faxnummer", 'fr-FR': u"fax bureau"},
'_$!<OtherFAX>!$_': {'en-US': u"_$!<OtherFAX>!$_", 'de-DE': u"_$!<OtherFAX>!$_", 'fr-FR': u"_$!<OtherFAX>!$_"},
'_$!<Pager>!$_': {'en-US': u"pager", 'de-DE': u"Pagernummer", 'fr-FR': u"biper"},
'_$!<Other>!$_':{'en-US': u"other phone", 'de-DE': u"anderes Telefon", 'fr-FR': u"autre"}
}

namesToNumberTypes = {
'de-DE': {'mobile': "_$!<Mobile>!$_", 'handy': "_$!<Mobile>!$_", 'zuhause': "_$!<Home>!$_", 'privat': "_$!<Home>!$_", 'arbeit': "_$!<Work>!$_"},
'fr-FR': {'mobile': "_$!<Mobile>!$_", 'gsm': "_$!<Mobile>!$_", 'portable': "_$!<Mobile>!$_", 'domicile': "_$!<Home>!$_", 'maison': "_$!<Home>!$_", 'travail': "_$!<Work>!$_", 'boulot': "_$!<Work>!$_"},
'en-US': {'work': "_$!<Work>!$_",'home': "_$!<Home>!$_", 'mobile': "_$!<Mobile>!$_"}
}

speakableDemitter={
'en-US': u", or ",
'de-DE': u', oder ',
'fr-FR': u', ou ',
}

errorNumberTypes= {
'de-DE': u"Ich habe dich nicht verstanden, versuch es bitte noch einmal.",
'en-US': u"Sorry, I did not understand, please try again.",
'fr-FR': u"Désolé, je n'ai pas compris, veuillez réessayer."
}

errorNumberNotPresent= {
'de-DE': u"Ich habe diese {0} von {1} nicht, aber eine andere.",
'en-US': u"Sorry, I don't have a {0} email from {1}, but another.",
'fr-FR': u"Désolé, je n'ai pas une adresse email de {0} pour {1}, mais une autre."
}


class mail(Plugin):

    def searchUserByName(self, personToLookup):
        search = PersonSearch(self.refId)
        search.scope = PersonSearch.ScopeLocalValue
        search.name = personToLookup
        answerObj = self.getResponseForRequest(search)
        if ObjectIsCommand(answerObj, PersonSearchCompleted):
            answer = PersonSearchCompleted(answerObj)
            return answer.results if answer.results != None else []
        else:
            raise StopPluginExecution("Unknown response: {0}".format(answerObj))
        return []

    def getNumberTypeForName(self, name, language):
        # q&d
        if name != None:
            if name.lower() in namesToNumberTypes[language]:
                return namesToNumberTypes[language][name.lower()]
            else:
                for key in numberTypesLocalized.keys():
                    if numberTypesLocalized[key][language].lower() == name.lower():
                        return numberTypesLocalized[key][language]
        return None

    def findPhoneForNumberType(self, person, numberType, language):
        # first check if a specific number was already requested
        phoneToCall = None
        if numberType != None:
            # try to find the phone that fits the numberType
            phoneToCall = filter(lambda x: x.label == numberType, person.emails)
        else:
            favPhones = filter(lambda y: y.favoriteVoice if hasattr(y, "favoriteVoice") else False, person.emails)
            if len(favPhones) == 1:
                phoneToCall = favPhones[0]
        if phoneToCall == None:
            # lets check if there is more than one number
            if len(person.emails) == 1:
                if numberType != None:
                    self.say(errorNumberNotPresent.format(numberTypesLocalized[numberType][language], person.fullName))
                phoneToCall = person.emails[0]
            else:
                # damn we need to ask the user which one he wants...
                while(phoneToCall == None):
                    rootView = AddViews(self.refId, temporary=False, dialogPhase="Clarification", scrollToTop=False, views=[])
                    sayit = responses['selectNumber'][language].format(person.fullName)
                    rootView.views.append(AssistantUtteranceView(text=sayit, speakableText=sayit, listenAfterSpeaking=True,dialogIdentifier="ContactDataResolutionDucs#foundAmbiguousPhoneNumberForContact"))
                    lst = DisambiguationList(items=[], speakableSelectionResponse="OK...", listenAfterSpeaking=True, speakableText="", speakableFinalDemitter=speakableDemitter[language], speakableDemitter=", ",selectionResponse="OK...")
                    rootView.views.append(lst)
                    for phone in person.emails:
                        try:
                            numberType = phone.label
                        except:
                            numberType = '_$!<Other>!$_'
                            phone.label = '_$!<Other>!$_'
                        item = ListItem()
                        item.title = ""
                        item.text = u"{0}: {1}".format(numberTypesLocalized[numberType][language], phone.emailAddress)
                        item.selectionText = item.text
                        item.speakableText = u"{0}  ".format(numberTypesLocalized[numberType][language])
                        item.object = phone
                        item.commands.append(SendCommands(commands=[StartRequest(handsFree=False, utterance=numberTypesLocalized[numberType][language])]))
                        lst.items.append(item)
                    answer = self.getResponseForRequest(rootView)
                    numberType = self.getNumberTypeForName(answer, language)
                    if numberType != None:
                        matches = filter(lambda x: x.label == numberType, person.emails)
                        if len(matches) == 1:
                            phoneToCall = matches[0]
                        elif person.emails[0] != None:
                            phoneToCall = person.emails[0]
                        else:
                            self.say(errorNumberTypes[language])
                    else:
                        self.say(errorNumberTypes[language])
        return phoneToCall

    def presentPossibleUsers(self, persons, language):
        root = AddViews(self.refId, False, False, "Clarification", [], [])
        root.views.append(AssistantUtteranceView(responses['select'][language], responses['select'][language], "ContactDataResolutionDucs#disambiguateContact", True))
        lst = DisambiguationList([], "OK!", True, "OK!", speakableDemitter[language], ", ", "OK!")
        root.views.append(lst)
        for person in persons:
            item = ListItem(person.fullName, person.fullName, [], person.fullName, person)
            item.commands.append(SendCommands([StartRequest(False, "^phoneCallContactId^=^urn:ace:{0}".format(person.identifier))]))
            lst.items.append(item)
        return root

    @register("en-US", u"(email)* (?P<recipient>[\w ]+) *about* (?P<subject>[\w ]+)")
    @register("fr-FR", u"(envoy(er|ez|é) un .?mail (a|à))* (?P<recipient>[\w ]+) *au sujet de* (?P<subject>[\w ]+)")
    def mail(self, speech, language, regex):
        personToCall = regex.group('recipient')
        subject = regex.group('subject')
        print personToCall
        numberType = ""
        numberType = self.getNumberTypeForName(numberType, language)
        persons = self.searchUserByName(personToCall)
        personToCall = None
        if len(persons) > 0:
            if len(persons) == 1:
                personToCall = persons[0]
            else:
                identifierRegex = re.compile("\^phoneCallContactId\^=\^urn:ace:(?P<identifier>.*)")
                #  multiple users, ask user to select
                while(personToCall == None):
                    strUserToCall = self.getResponseForRequest(self.presentPossibleUsers(persons, language))
                    self.logger.debug(strUserToCall)
                    # maybe the user clicked...
                    identifier = identifierRegex.match(strUserToCall)
                    if identifier:
                        strUserToCall = identifier.group('identifier')
                        self.logger.debug(strUserToCall)
                    for person in persons:
                        if person.fullName == strUserToCall or person.identifier == strUserToCall:
                            personToCall = person
                    if personToCall == None:
                        # we obviously did not understand him.. but probably he refined his request... call again...
                        self.say(errorNumberTypes[language])

            if personToCall != None:
		personAttribute=PersonAttribute()
		targetEmailAdress = self.findPhoneForNumberType(personToCall, numberType, language)
		personAttribute.data = targetEmailAdress.emailAddress
		personAttribute.displayText = personToCall.fullName
		PersonObject = Person()
		PersonObject.identifier = personToCall.identifier
		personAttribute.object=PersonObject
		self.say(u"Création de l'email...", " ")
		email = EmailEmail()
		email.subject = subject.title()
		email.recipientsTo = [personAttribute]
		email.outgoing = True
		email.type = "New"
		EmailDomain = DomainObjectCreate(self.refId, email)
		answer = self.getResponseForRequest(EmailDomain)

		if ObjectIsCommand(answer, DomainObjectCreateCompleted):
		      identifier = DomainObjectCreateCompleted(answer)
		      self.logger.debug("DomainObject identifier : {0}".format(identifier.identifier))
		      DomainIdentifier = identifier.identifier
		else:
		      raise StopPluginExecution("Unknown response: {0}".format(answer))
		email.identifier = DomainIdentifier
		EmailView = AddViews(self.refId, dialogPhase="Clarification")

		Ask = AssistantUtteranceView(u"Que voulez-vous dire à {0} ?".format(personToCall.firstName), u"Que voulez-vous dire à {0} ?".format(personToCall.firstName), listenAfterSpeaking=True)

		MyEmailSnippet = 0
		MyEmailSnippet = EmailSnippet()
		MyEmailSnippet.emails = [email]
		EmailView.views = [Ask, MyEmailSnippet]
		EmailView.scrollToTop = True
		print "Sending view ..."
		messageFU = self.getResponseForRequest(EmailView)
		print messageFU


		DomainUpdate = DomainObjectUpdate(self.refId)

		UpdateField = EmailEmail()
		UpdateField.message = messageFU
		DomainUpdate.setFields = UpdateField

		DomainUpdate.addFields = EmailEmail()

		UpdateDomainIdentifier = EmailEmail()
		UpdateDomainIdentifier.identifier = DomainIdentifier
		DomainUpdate.identifier = UpdateDomainIdentifier
		time.sleep(2)
		print "Sending update request ..."
		DomainUpdateAnswer = self.getResponseForRequest(DomainUpdate)

		if ObjectIsCommand(DomainUpdateAnswer, DomainObjectUpdateCompleted):
		      print "Recived DomainObjectUpdateCompleted !"
		else:
		      raise StopPluginExecution("Unknown response: {0}".format(answer))

		DomainRetrieve = DomainObjectRetrieve(self.refId)
		DomainObjectRetrieve.identifiers=[DomainIdentifier]
		print "Sending Retrieve object ..."
		DomainRetrieveAnswer = self.getResponseForRequest(DomainRetrieve)

		if ObjectIsCommand(DomainRetrieveAnswer, DomainObjectRetrieveCompleted):
		      print "Recived DomainObjectRetrieveCompleted !"
		else:
		      raise StopPluginExecution("Unknown response: {0}".format(answer))

		FinallAsk = AssistantUtteranceView("Je l'envoie ?", "Je l'envoie ?", listenAfterSpeaking=True)

		FinallEmail = EmailEmail()
		FinallEmail.identifier = DomainIdentifier

		FinallSnippet = EmailSnippet()
		FinallSnippet.emails = [FinallEmail]

		FinallView = AddViews(self.refId, dialogPhase="Clarification")
		FinallView.views = [FinallAsk, FinallSnippet]
		FinallView.scrollToTop = True

		ReadyToSend = self.getResponseForRequest(FinallView).lower()

		if(ReadyToSend == u"oui" or ReadyToSend == u"by" or ReadyToSend == u"il est" or ReadyToSend == u"bien sûr"):
		  CommitEmail = EmailEmail()
		  CommitEmail.identifier = DomainIdentifier

		  Commit = DomainObjectCommit(self.refId)
		  Commit.identifier = CommitEmail

		  CommitAnswer = self.getResponseForRequest(Commit)
		  print "Recived answer !"
		  if ObjectIsCommand(CommitAnswer, DomainObjectCommitCompleted):
		      print "Recived DomainObjectCommitCompleted !"
		      self.say(u"J'ai envoyé votre mail !")
		  else:
		      raise StopPluginExecution("Unknown response: {0}".format(answer))
		else:
		  self.say("OK, je ne l'envoie pas.")
		self.complete_request()

        self.say(responses['notFound'][language])
        self.complete_request()










