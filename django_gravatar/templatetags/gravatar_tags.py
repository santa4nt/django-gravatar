import re
import urllib
import hashlib

from django import template
from django.conf import settings


EMAIL_RE = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', re.IGNORECASE)
GRAVATAR_URL_PREFIX = 'http://www.gravatar.com/avatar/'
DEFAULT_PARAMS = \
{
    # api_key:  (gravatar_key, value),
    'size':     ('s', 80),          # value is in [1,512]
    'rating':   ('r', 'g'),         # 'pg', 'r', or 'x'
    'default':  ('d', 'identicon'), # 'monsterid', 'wavatar', '404', or escaped URI
}

register = template.Library()


class GravatarURLNode(template.Node):

    def __init__(self, email, params):
        self.params = template.Variable(params)
        self.email = email

    def render(self, context):
        try:
            params = self.params.resolve(context)

            if EMAIL_RE.match(self.email):  # try matching an address string literal
                email = self.email
            else:                           # treat as a variable
                email = template.Variable(self.email).resolve(context)
                if not EMAIL_RE.match(email):
                    raise template.TemplateSyntaxError('Not a valid email address.')
        except template.VariableDoesNotExist:
            return ''
        except template.TemplateSyntaxError:
            if settings.DEBUG:
                raise
            else:
                return ''

        # now, we generate the gravatar url
        # step 1: get a hex hash of the email address
        email_hash = hashlib.md5(email).hexdigest()

        # step 2a: build a canonized parameters dictionary
        actual_params = {}
        default_keys = DEFAULT_PARAMS.keys()
        for key, value in params.items():
            if key in default_keys:
                k, default_value = DEFAULT_PARAMS[key]
                # skip parameters whose values are defaults,
                # assume these values are mirroring Gravatar's defaults
                if value != default_value:
                    actual_params[k] = value

        # step 2b: validate the canonized parameters dictionary
        # silently drop parameter when the value is not valid
        for key, value in actual_params.items():
            if key == 's':
                if value < 1 or value > 512:
                    del actual_params[key]
            elif key == 'r':
                if value.lower() not in ('g', 'pg', 'r', 'x'):
                    del actual_params[key]
            # except when the parameter key is 'd': replace with 'identicon'
            elif key == 'd':
                if value.lower() not in ('identicon', 'monsterid', 'wavatar', '404'):
                    # TODO: validate for URI
                    if True:    # TODO: if not a valid URI
                        actual_params[key] = 'identicon'
                    else:       # TODO: valid URI, encode it
                        # encode special chars in URI
                        pass
        
        # set parameter d=identicon if missing
        try:
            actual_params['d']
        except KeyError:
            actual_params['d'] = 'identicon'

        # step 3: encode params
        params_encode = urllib.urlencode(actual_params)

        # step 4: form the gravatar url
        gravatar_url = GRAVATAR_URL_PREFIX + email_hash
        if params_encode:
            gravatar_url += '?' + params_encode

        return gravatar_url


@register.tag(name="gravatar_url")
def get_gravatar_url(parser, token):
    """For template tag: {% gravatar_url <email> <params> %}

    Where <params> is an object or a dictionary (variable), and <email>
    is a string object (variable) or a string (literal).
    """
    try:
        tag_name, email, params = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires two arguments.' %
                token.contents.split()[0])

    # if email is quoted, parse as a literal string
    if email[0] in ('"', "'") or email[-1] in ('"', "'"):
        if email[0] == email[-1]:
            email = email[1:-1]
        else:
            raise template.TemplateSyntaxError(
                    "%r tag's first argument is in unbalanced quotes." % tag_name)

    return GravatarURLNode(email, params)