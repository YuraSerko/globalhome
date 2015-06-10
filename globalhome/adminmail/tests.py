# -*- coding=utf-8 -*-

import unittest
from process import src2cid, MassMailLetterWithCommonSubject

class SrcToCidTestCase(unittest.TestCase):

    def setUp(self):
        self.string_from = u"""Привет, <a href="/admin/mail/"><img src="/media/uploads/mails/embed/qwerty_qwerty.png" alt="image" /></a>"""
        self.string_to = u"""Привет, <a href="/admin/mail/"><img src="cid:img0" alt="image" /></a>"""
    
    def testEqual(self):
        s = src2cid(self.string_from)
        self.assertEquals(self.string_to, s[0])
        print s[0], s[1], type(s[0])
    
    def testSending(self):
        m = MassMailLetterWithCommonSubject('INVITE','ru', {'registrarion_url':'', 'registration_key':'key'}, 'admin@admin.loc', ['test@test.loc'])
        m.start()
    
    def runTest(self):
        self.setUp()
        #self.testEqual()
        self.testSending()
        
