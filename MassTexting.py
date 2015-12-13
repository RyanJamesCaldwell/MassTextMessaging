##############################################################################################################
##############################################################################################################
######                                     Mass Text Messaging Program                                  ######
######                                                                                                  ######
###### Program Description: Send email/text message to email address, then the contents of that email   ######
######                      will be sent out to a user defined contact list.                            ######
######                                                                                                  ######
###### Created by: Ryan Caldwell, 2015.                                                                 ######
##############################################################################################################
##############################################################################################################

##      Mobile Carrier 	             SMS gateway domain
#############################################################
##      AT&T	                     txt.att.net
##      Cricket	                     mms.mycricket.com
##      Sprint	                     messaging.sprintpcs.com
##      T-Mobile                     tmomail.net
##      U.S. Celular	             email.uscc.net
##      Verizon Wireless             vtext.com
##      Virgin Mobile                vmobl.com


import smtplib, poplib, email, time

def hasNewEmail(connectedPopServer, numEmails):
    #If there is a new email detected, return true. Else, return false.
    
    hasNewEmail = False

    if(numEmails > 0):
        hasNewEmail = True

    return hasNewEmail



def connectToPopServer():
    #Returns a successful connection to a GMail pop server

    try:
        popServer = poplib.POP3() #pop server to connect to 
        popServer.user() #your email address
        popServer.pass_() #your password
        print "Successfully connected to pop server"
        return popServer
    except:
        print "Failed to connect to pop server"



def connectToSMTPServer():
    #Returns a connection to a GMail SMTP server
    try:
        connectedServer = smtplib.SMTP()  #SMTP server to connect to 
        connectedServer.ehlo()
        connectedServer.starttls()
        connectedServer.login() #email address and password
        print "Successfully connected to SMTP server"
        return connectedServer
    except:
        "Failed to connect to SMTP server"


def retrieveEmail(connectedPopServer, numEmails):
    #If there is a new email, return the new email

    try:
        email = connectedPopServer.retr(numEmails)
        connectedPopServer.dele(numEmails) #mark as read
        connectedPopServer.quit()
        return email
    except:
        print "Could not properly retrieve email."




def parseEmailForText(email):
    #Gets the text and message sender information from the elementList provided by the pop.stat() method
    
    elementList = email[-2]
    
    for element in elementList:
        if element.startswith("mass") or element.startswith("Mass"):
            emailText = element
            break
        else:
            emailText = None

            
    return emailText



def parseEmailForSender(email):
    #Returns the cell phone number of who sent the text message
    
    elementList = email[-2]
    massSentBy = elementList[7]

    return massSentBy





def sendTextMessage(connectedSMTPServer, massContents):
    #Connects to the SMTP server and sends the text message

    sendFrom = '' #Email address that the text is being sent from
    sendTo = [] #(Can be) large list of phone numbers to send text message to

                
    massLength = len(massContents)
    textsNeededToSend = 1 #at least one message will be sent

    
    if(massLength > 149):
        textsNeededToSend = (massLength / 149) + 1

    while textsNeededToSend > 0:
        if(textsNeededToSend > 1):
            specificMassContents = massContents[:149]
        else:
            specificMassContents = massContents
            
        message = """\From: %s
                     \nTo: %s
                     \n\n%s
        """ % (sendFrom, ", ".join(sendTo), specificMassContents)
        
        try:
            connectedSMTPServer.sendmail(sendFrom, sendTo, message)
            print 'Mass text sent successfully.'
        except:
            print "Error. Mass text was not sent."

        textsNeededToSend = textsNeededToSend - 1
        massContents = massContents[149:]





def sendReport(connectedSMTPServer, massContents, senderInfo):
    #Basically the same as sendTextMessage() with information about who sent the text message.
    #The reason for getting the sender information is so that I can monitor who is sending texts.
    
    sendFrom = '' #Email address that the report is being sent from
    sendTo = []  #Email address to send the mass to

                # Prepare actual message
    message = """\From: %s
                 \nTo: %s
                 \n\n%s
                 \n\nSender cell phone number: %s
    """ % (sendFrom, ", ".join(sendTo), massContents, senderInfo)
    
    try:
        connectedSMTPServer.sendmail(sendFrom, sendTo, message)
        connectedSMTPServer.close()
        print 'Report sent successfully.'
    except:
        print "Error. Report was not sent."




if __name__ == "__main__":

    
    while True:
        
        successfullyConnected = False
        
        while successfullyConnected == False:               #If for any reason we lose connection, don't let the program crash.
            connectedPopServer = connectToPopServer()       #Keep attempting connections until a successful one has been made.
            if(connectedPopServer != None):
                successfullyConnected = True
                
        (numEmails, sizeOfInbox) = connectedPopServer.stat()
        
        if(hasNewEmail(connectedPopServer, numEmails)):
            print "New mail found."
            newEmail = retrieveEmail(connectedPopServer, numEmails)
            textToMass = parseEmailForText(newEmail)
            senderInfo = parseEmailForSender(newEmail)
            
            if(textToMass != None):     #check that the text sent to the server is a relevant text
                print textToMass
                connectedSMTPServer = connectToSMTPServer()
                sendTextMessage(connectedSMTPServer, textToMass)
                sendReport(connectedSMTPServer, textToMass, senderInfo)
            else:
                print "Empty mass text. Not sending."
        else:
            print "No new mail. Searching again..."
            time.sleep(610)
