#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import django_gravatar.templatetags.gravatar_tags as gt


class URLTest(unittest.TestCase):

    def setUp(self):
        pass

    def _assert_mapped(self, email, params, url):
        built_url = gt._build_gravatar_url(email, params)
        self.assertEqual(built_url, url, '%s maps to %s' \
                % (repr(email), repr(built_url)))

    def testEmail(self):
        valid_emails = \
        [
            'santa.ant@me.com',
            'Santa.Ant@Me.Com',
            '   santa.ant@me.com',
            'santa.ant@me.com   ',
            '   Santa.Ant@Me.Com    ',
        ]

        invalid_emails = \
        [
            '',
            '   ',
            '\/<>""',
            '@.com',
            'santa.ant.com',
            'santa@ant@com',
        ]

        # the gravatar url of valid_emails
        gr_url = 'http://www.gravatar.com/avatar/73166d43fc3b2dc5f56669ce27984ad0?d=identicon'

        for email in valid_emails:
            self._assert_mapped(email, {}, gr_url)

        for email in invalid_emails:
            self._assert_mapped(email, {}, '')

    def testParams(self):
        self.assertTrue(True)

    def tearDown(self):
        pass
