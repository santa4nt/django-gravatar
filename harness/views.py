from django.http import Http404
from django.shortcuts import render_to_response

def email(request, email):
    """Render a template with the email address generating
    Gravatar images.
    """
    return render_to_response('email.html',
            {'email': email, 'params': {
                'size': 120,
                'default': 'wavatar',
                'rating': 'pg',
            }})
