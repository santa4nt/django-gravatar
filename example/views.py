from django.http import Http404
from django.shortcuts import render_to_response

def email(request, email):
    """Render a template with the email address generating
    Gravatar images.
    """
    params = {}
    params['size'] = 120
    params['default'] = 'http://example.com/images/example.jpg'
    params['rating'] = 'pg'

    return render_to_response('email.html',
            {'email': email, 'params': params})
