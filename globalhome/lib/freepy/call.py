#!/usr/bin/python
# script to parse email for phonenumber in subject or body, and call back with extension
# Replace DOMAIN with the value of $${domain}
# Replace EXTENSION with the value of the application (&rxfax()) or extension (5000)
# Replace PASSWORD with the password for the email2callback user extension

import sys
import os
import email.Parser
import types
import re
import syslog
import string
import sys

sys.path.append('/opt/freeswitch/scripts/socket')
sys.path.append('/opt/freeswitch/scripts/socket/freepy')
from ESL import *
from fshelper import *

def initiateCallback(from_numb, to_numb, file_name):
    outgoing_number="unknown"
    print "Vowli v initiateCallback !!!"
    # first try to parse the incoming email
    #message = email.message_from_file(sys.stdin)

    #
    #  process the message here
    #
    #syslog.syslog('Received mail from "%s", subject: "%s"' % (message.get('From'), message.get('Subject') ))

    #subject = message.get('Subject')
    #m = re.match('callback (\d*)', subject)
    #if m:
    #    outgoing_number = m.group(1)  

    #msg = message.get_payload()
    #m = re.match('callback (\d*)', msg)
    #if m:
    #        outgoing_number = m.group(1)
   
    syslog.syslog('Making outgoing call to "1000002"') 

    fshelper = FsHelper(host="0.0.0.0",
                        passwd="ClueCon",
                        port=8021)        

    con = ESLconnection("localhost","8021","ClueCon")
#are we connected?

    if con.connected:
        con.events("plain", "CHANNEL_DESTROY");
        print "con.connected = yes"

    #my $e = $con->recvEventTimed(100);
    #e = con.recvEvent()
    #e = con.getHeader("Caller-Callee-ID-Name")
    def worked(result):
        print "Originate succeeded: %s" % result
        print "rabotaet!!!!!!\n"
        reactor.stop()

    def failed(failure):
        print "failed: %s" % failure
        print "ne rabotaet!!!\n"
        reactor.stop()

    dest_ext_app = "&txfax(%s)" % file_name
    #party2dial="[sip_auth_username=email2callback,sip_auth_password=PASSWORD]sofia/external/%s@192.168.0.251" % outgoing_number
    party2dial="%s" % to_numb
    print "call py!!!!\n"
    d2 = fshelper.originate(party2dial=party2dial, dest_ext_app=dest_ext_app, bgapi=True)
    print "originate prowel!!!!!\n"
    d2.addCallback(worked)
    d2.addErrback(failed)
    #print "d2=%s" % dir (d2)
    print "CallBack i Errback prowel!!!\n"
    reactor.run()
    print "Reactorrun!!!!\n"
    while 1:
        e = con.recvEvent()
        if e:
            #print e.serialize()
            if e.getHeader("Caller-Caller-ID-Number")==from_numb:
                if e.getHeader("variable_fax_success")=="1":
                    print "Fax yspewno otpravlen: "
                    print e.getHeader("variable_fax_success")
                    break
                else:
                    if e.getHeader("variable_originate_disposition")=="USER_NOT_REGISTERED":
                        print "Nomer ne zaregestrirovan !!!"
                    else:
                        if e.getHeader("variable_hangup_cause")=="ORIGINATOR_CANCEL":
                            print "Nomer ne otve4aet !!!"
                        if e.getHeader("variable_hangup_cause")=="USER_BUSY":
                            print "Nomer zan9t !!!"
                    print e.getHeader("variable_fax_success")
                    print e.getHeader("variable_fax_result_text")
                    print e.getHeader("variable_originate_disposition")
                    print e.getHeader("variable_hangup_cause")
                    print "Fax ne dostavlen !!!"
                    break 
            #break
        #if e:
        #    print e.serialize()





    '''def worked(result):
        print "Originate succeeded: %s" % result
        print "rabotaet!!!!!!\n"
        reactor.stop()
        
    def failed(failure):
        print "failed: %s" % failure
        print "ne rabotaet!!!\n"
        reactor.stop()


    dest_ext_app = "&txfax(/usr/rxfax.tiff)"
    #party2dial="[sip_auth_username=email2callback,sip_auth_password=PASSWORD]sofia/external/%s@192.168.0.251" % outgoing_number
    party2dial="sofia/internal/1000002@192.168.0.251"
    print "call py!!!!\n"
    d2 = fshelper.originate(party2dial=party2dial, dest_ext_app=dest_ext_app, bgapi=True)
    print "originate prowel!!!!!\n"
    d2.addCallback(worked)
    d2.addErrback(failed)
    print "d2=%s" % dir (d2)
    print "CallBack i Errback prowel!!!\n"
    reactor.run()    
    print "Reactorrun!!!!\n"  '''


if __name__=="__main__":
    from_numb = "0000000000"
    to_numb = "sofia/internal/1000002@192.168.0.251"
    file_name = "/usr/rxfax.tiff"
    initiateCallback(from_numb, to_numb, file_name)