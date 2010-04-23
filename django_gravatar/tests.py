#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import django_gravatar.templatetags.gravatar_tags as gt


class URLTest(unittest.TestCase):

    def setUp(self):
        pass

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
        gr_url = 'http://www.gravatar.com/avatar/73166d43fc3b2dc5f56669ce27984ad0'

        def _assert_mapped(email, url):
            built_url = gt._build_gravatar_url(email, {})
            self.assertEqual(built_url, url, '%s maps to %s' \
                    % (repr(email), repr(built_url)))

        for email in valid_emails:
            _assert_mapped(email, gr_url)

        for email in invalid_emails:
            _assert_mapped(email, '')

    def testParams(self):
        email = 'santa.ant@me.com'
        url = 'http://www.gravatar.com/avatar/73166d43fc3b2dc5f56669ce27984ad0'

        # 2-tuple: (<params as dict>, <url encoded params>)
        dict_params_set = \
        [
            ({'size':120}, 
                    's=120'),
            ({'size':120, 'default':'identicon'}, 
                    's=120&d=identicon'),
            ({'size':120, 'default':''}, 
                    's=120'),
            ({'size':120, 'rating':'pg', 'default':'identicon'},
                    's=120&r=pg&d=identicon'),
            ({'size':80}, 
                    ''),
            ({'size':80, 'default':'identicon'},
                    'd=identicon'),
            ({'size':80, 'rating':'r', 'default':'wavatar'},
                    'r=r&d=wavatar'),
            ({'size':120, 'rating': 'g', 'default':'404'},
                    's=120&d=404'),
            ({'size':513},
                    ''),
            ({'size':0, 'default':'monsterid'},
                    'd=monsterid'),
            ({'size':120, 'rating':'x'},
                    's=120&r=x'),
            ({'default':'nonexistent'},
                    ''),
            ({'default':'nonexistent', 'size':80},
                    ''),
            ({'default':'nonexistent', 'size':80, 'rating':'f'},
                    ''),
            ({'default':'nonexistent', 'size':120},
                    's=120'),
            ({'default':'nonexistent', 'size':120, 'rating':'f'},
                    's=120'),
            ({'rating':'g'},
                    ''),
            ({'rating':'r'},
                    'r=r'),
            ({'rating':'g', 'default':'identicon'},
                    'd=identicon'),
            ({'rating':'b', 'size':120},
                    's=120'),
            ({'default':'http://example.com/images/example.jpg'},
                    'd=http%3A%2F%2Fexample.com%2Fimages%2Fexample.jpg'),
            ({'default':'http:/example.com/images/example.jpg'},
                    ''),
            ({'default':'http//example.com/images/example.jpg'},
                    ''),
        ]

        class Params:
            pass

        # make the same thing as above, with object attributes
        obj_params_set = []
        for (dict_params, url_params) in dict_params_set:
            obj_params = Params()
            for k, v in dict_params.items():
                setattr(obj_params, k, v)
            obj_params_set.append((obj_params, url_params))

        for params, url_encode in (dict_params_set + obj_params_set):
            built_url = gt._build_gravatar_url(email, params)
            if url_encode:
                match = url + '?' + url_encode
            else:
                match = url
        
            self.assertEqual(built_url, match)

    def tearDown(self):
        pass
