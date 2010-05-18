import re
import urllib
import hashlib

from django import template
from django.conf import settings


URL_RE = re.compile(r'^https?://([-\w\.]+)+(:\d+)?(/([\w/_\.]*(\?\S+)?)?)?',
        re.IGNORECASE)
EMAIL_RE = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$',
        re.IGNORECASE)
GRAVATAR_URL_PREFIX = 'http://www.gravatar.com/avatar/'
DEFAULT_PARAMS = \
{
    # api_key:  (gravatar_key, value),
    'size':     ('s', 80),          # value is in [1,512]
    'rating':   ('r', 'g'),         # 'pg', 'r', or 'x'
    'default':  ('d', ''),          # 'identicon', 'monsterid', 'wavatar', '404', or escaped URI
}

register = template.Library()


def _build_gravatar_url(email, params):
    """Generate a Gravatar URL.
    
    """
    # step 1: get a hex hash of the email address
    email = email.strip().lower().encode('utf-8')
    if not EMAIL_RE.match(email):
        return ''

    email_hash = hashlib.md5(email).hexdigest()

    # step 2a: build a canonized parameters dictionary
    if not type(params).__name__ == 'dict':
        params = params.__dict__

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
                if not URL_RE.match(value): # if not a valid URI
                    del actual_params[key]
                else:                       # valid URI, encode it
                    actual_params[key] = value  # urlencode will encode it later
    
    # step 3: encode params
    params_encode = urllib.urlencode(actual_params)

    # step 4: form the gravatar url
    gravatar_url = GRAVATAR_URL_PREFIX + email_hash
    if params_encode:
        gravatar_url += '?' + params_encode

    return gravatar_url


class GravatarURLNode(template.Node):

    def __init__(self, email, params):
        self.email = email
        self.params = params

    def render(self, context):
        try:
            if self.params:
                params = template.Variable(self.params).resolve(context)
            else:
                params = {}

            # try matching an address string literal
            email_literal = self.email.strip().lower()
            if EMAIL_RE.match(email_literal):
                email = email_literal
            # treat as a variable
            else:
                email = template.Variable(self.email).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        # now, we generate the gravatar url
        return _build_gravatar_url(email, params)


@register.tag(name="gravatar_url")
def get_gravatar_url(parser, token):
    """For template tag: {% gravatar_url <email> <params> %}

    Where <params> is an object or a dictionary (variable), and <email>
    is a string object (variable) or a string (literal).

    """
    try:
        tag_name, email, params = token.split_contents()
    except ValueError:
        try:
            tag_name, email = token.split_contents()
            params = None
        except ValueError:
            raise template.TemplateSyntaxError('%r tag requires one or two arguments.' %
                    token.contents.split()[0])

    # if email is quoted, parse as a literal string
    if email[0] in ('"', "'") or email[-1] in ('"', "'"):
        if email[0] == email[-1]:
            email = email[1:-1]
        else:
            raise template.TemplateSyntaxError(
                    "%r tag's first argument is in unbalanced quotes." % tag_name)

    return GravatarURLNode(email, params)
