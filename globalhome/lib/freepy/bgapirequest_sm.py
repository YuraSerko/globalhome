# DO NOT EDIT.
# generated by smc (http://smc.sourceforge.net/)
# from file : bgapirequest.sm

import statemap


class BgApiRequestState(statemap.State):

    def Entry(self, fsm):
        pass

    def Exit(self, fsm):
        pass

    def BlankLine(self, fsm):
        self.Default(fsm)

    def CommandReply(self, fsm):
        self.Default(fsm)

    def JobUuid(self, fsm):
        print "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY\n"
        self.Default(fsm)

    def ProcessLine(self, fsm, line):
        self.Default(fsm)

    def ReplyText(self, fsm):
        self.Default(fsm)

    def Default(self, fsm):
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write('TRANSITION   : Default\n')
        msg = "\n\tState: %s\n\tTransition: %s" % (
            fsm.getState().getName(), fsm.getTransition())
        raise statemap.TransitionUndefinedException, msg

class MainMap_Default(BgApiRequestState):

    def BlankLine(self, fsm):
        ctxt = fsm.getOwner()
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.Default.BlankLine()\n")

        endState = fsm.getState()
        fsm.clearState()
        try:
            ctxt.setRequestFinished()
            ctxt.errbackDeferred("Protocol failure - was not expecting blank line")
        finally:
            fsm.setState(endState)

    def CommandReply(self, fsm):
        ctxt = fsm.getOwner()
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.Default.CommandReply()\n")

        endState = fsm.getState()
        fsm.clearState()
        try:
            ctxt.setRequestFinished()
            ctxt.errbackDeferred("Protocol failure - was not expecting command reply")
        finally:
            fsm.setState(endState)

    def ReplyText(self, fsm):
        ctxt = fsm.getOwner()
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.Default.ReplyText()\n")

        endState = fsm.getState()
        fsm.clearState()
        try:
            ctxt.setRequestFinished()
            ctxt.errbackDeferred("Protocol failure - was not expecting reply text")
        finally:
            fsm.setState(endState)

    def ProcessLine(self, fsm, line):
        ctxt = fsm.getOwner()
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.Default.ProcessLine(line)\n")

        endState = fsm.getState()
        fsm.clearState()
        try:
            ctxt.setRequestFinished()
            ctxt.errbackDeferred("Protocol failure handling bgapi response - was not expecting line needing to be processed")
        finally:
            fsm.setState(endState)

class MainMap_Startup(MainMap_Default):

    def CommandReply(self, fsm):
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.Startup.CommandReply()\n")

        fsm.getState().Exit(fsm)
        fsm.setState(MainMap.ApiResponseStarted)
        fsm.getState().Entry(fsm)

class MainMap_ApiResponseStarted(MainMap_Default):

    def ReplyText(self, fsm):
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.ApiResponseStarted.ReplyText()\n")

        fsm.getState().Exit(fsm)
        fsm.setState(MainMap.GotReplyText)
        fsm.getState().Entry(fsm)

class MainMap_GotReplyText(MainMap_Default):

    def BlankLine(self, fsm):
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.GotReplyText.BlankLine()\n")


    def JobUuid(self, fsm):
        print "YYYYYYYYYYYYYYYYY3333\n"
        ctxt = fsm.getOwner()
        if fsm.getDebugFlag() == True:
            fsm.getDebugStream().write("TRANSITION   : MainMap.GotReplyText.JobUuid()\n")

        fsm.getState().Exit(fsm)
        fsm.clearState()
        try:
            ctxt.setRequestFinished()
            ctxt.callOrErrback()
        finally:
            fsm.setState(MainMap.Startup)
            fsm.getState().Entry(fsm)

class MainMap:

    Startup = MainMap_Startup('MainMap.Startup', 0)
    ApiResponseStarted = MainMap_ApiResponseStarted('MainMap.ApiResponseStarted', 1)
    GotReplyText = MainMap_GotReplyText('MainMap.GotReplyText', 2)
    Default = MainMap_Default('MainMap.Default', -1)

class BgApiRequest_sm(statemap.FSMContext):

    def __init__(self, owner):
        statemap.FSMContext.__init__(self)
        self._owner = owner
        self.setState(MainMap.Startup)
        MainMap.Startup.Entry(self)

    def BlankLine(self):
        self._transition = 'BlankLine'
        self.getState().BlankLine(self)
        self._transition = None

    def CommandReply(self):
        self._transition = 'CommandReply'
        self.getState().CommandReply(self)
        self._transition = None

    def JobUuid(self):
        print "YYYYYYYYYYYYYYYYYY2222\n"
        self._transition = 'JobUuid'
        self.getState().JobUuid(self)
        self._transition = None

    def ProcessLine(self, *arglist):
        self._transition = 'ProcessLine'
        self.getState().ProcessLine(self, *arglist)
        self._transition = None

    def ReplyText(self):
        self._transition = 'ReplyText'
        self.getState().ReplyText(self)
        self._transition = None

    def getState(self):
        if self._state == None:
            raise statemap.StateUndefinedException
        return self._state

    def getOwner(self):
        return self._owner
