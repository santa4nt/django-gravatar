#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from django import template
from django.template import Context, Template
from django_gravatar.templatetags import gravatar_tags as gt
from django_gravatar.templatetags.gravatar_tags import get_gravatar_url


register = template.Library()

GR_URLS = \
{
    'santa.ant@me.com': 'http://www.gravatar.com/avatar/73166d43fc3b2dc5f56669ce27984ad0',
}


class URLTest(unittest.TestCase):
    """This test class exercises the logic of building a Gravatar URL
    in gravatar_tags._build_gravatar_url function.

    """

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

        def _assert_mapped(email, url):
            built_url = gt._build_gravatar_url(email, {})
            self.assertEqual(built_url, url, '%s maps to %s' \
                    % (repr(email), repr(built_url)))

        for email in valid_emails:
            _assert_mapped(email, GR_URLS['santa.ant@me.com'])

        for email in invalid_emails:
            _assert_mapped(email, '')

    def testParams(self):
        email = 'santa.ant@me.com'
        url = GR_URLS[email]

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


class TemplateTest(unittest.TestCase):
    """This test class exercises the template rendering logic in
    templatetags.gravatar_tags module.

    """

    def setUp(self):
        self.template_tag = 'gravatar_url'
        template.libraries['django.templatetags.%s' % self.template_tag] = register
        register.tag(name=self.template_tag, compile_function=get_gravatar_url)

    def _render_template(self, template_string, context={}):
        t = Template(template_string)
        c = Context(context)

        return t.render(c)

    def testSyntax(self):
        """This unit test exercises the parsing of the custom template tag
        syntax.

        """
        template_tag = self.template_tag
        base = '{%% load %s %%}' % template_tag

        email = 'santa.ant@me.com'
        render = GR_URLS[email]

        valid_tags = \
        [
            '{% gravatar_url santa.ant@me.com %}',
            '{% gravatar_url "santa.ant@me.com" %}',
            "{% gravatar_url ' santa.ant@me.com     ' %}",
        ]

        invalid_tags = \
        [
            '{% gravatar_url %}',
            '   {% gravatar_url %}  ',
            '{% gravatar_url "santa.ant@me.com" params too_many_args %}     ',
        ]

        for tag in valid_tags:
            template_string = base + tag
            rendered = self._render_template(template_string)

            self.assertEqual(rendered, render,
                    '%s renders to %s, not %s' \
                    % (repr(template_string), repr(rendered), repr(render)))

        for tag in invalid_tags:
            template_string = base + tag

            try:
                rendered = self._render_template(template_string)
            except template.TemplateSyntaxError:
                self.assertTrue(True)
            else:
                self.fail('%s renders to %s. It should have raised a TemplateSyntaxError.' \
                        % (repr(template_string), repr(rendered)))

    def testRenderEmails(self):
        """This unit test exercises the rendering of `{% gravatar_url <email> %}`
        tag, given literal or variable email strings.

        """
        template_tag = self.template_tag
        base = '{%% load %s %%}' % template_tag

        valid_literal_emails = \
        [
            'santa.ant@me.com',
            '"santa.ant@me.com"',
            '"  santa.ant@me.com"',
            "'santa.ant@me.com  '",
        ]

        unbalanced_literal_emails = \
        [
            '"santa.ant@me.com',
            "'santa.ant@me.com",
            'santa.ant@me.com"',
            "santa.ant@me.com'",
            "'santa.ant@me.com    ",
            '"santa.ant@me.com    ',
            "   'santa.ant@me.com",
            '   "santa.ant@me.com    ',
        ]

        variable_names = \
        [
            'email',
            'Email',
            '   eMail',
            'emaIl  ',
            '   EmaiL   ',
        ]

        def _test_render_literal(email, render):
            # {% gravatar_url <email> %}
            template_string = base + ('{%% %s %s %%}' % (template_tag, email))
            rendered = self._render_template(template_string)

            self.assertEqual(rendered, render,
                    '%s does not render to %s' % (repr(template_string), repr(render)))

        def _test_render_variable(varname, email, render):
            template_string = base + ('{%% %s %s %%}' % (template_tag, varname))
            rendered = self._render_template(template_string, {varname.strip(): email})

            self.assertEqual(rendered, render,
                    '%s does not render to %s; {%s: %s}' \
                    % (repr(template_string), repr(render), repr(varname), repr(email)))

        valid_email = 'santa.ant@me.com'
        render = GR_URLS[valid_email]

        for email in valid_literal_emails:
            _test_render_literal(email, render)

        for variable in variable_names:
            _test_render_variable(variable, valid_email, render)

        for email in unbalanced_literal_emails:
            # quote-unbalanced email literal should throw a TemplateSyntaxError
            template_string = base + ('{%% %s %s %%}' % (template_tag, email))

            try:
                rendered = self._render_template(template_string)
            except template.TemplateSyntaxError:
                self.assertTrue(True)
            else:
                self.fail('%s renders to %s. It should have raised a TemplateSyntaxError.' \
                        % (repr(template_string), repr(rendered)))

            # malformed email stored in a variable maps to empty string
            for variable in variable_names:
                _test_render_variable(variable, email, '')

    def tearDown(self):
        pass
