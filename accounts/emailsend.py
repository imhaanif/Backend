import sys 
sys.path.append('..')

import  django
import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'app.settings'
django.setup()
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from accounts.models import User
from django.contrib.auth.tokens import default_token_generator


# user = User.objects.get(slug='farhanmyslug')
# x = urlsafe_base64_encode(force_bytes(user.slug))
# tkn = default_token_generator.make_token(user)
# print(default_token_generator.check_token(user, tkn))

# print(x)
# print(force_text(urlsafe_base64_decode(x)))
activation_link = "siteurl"

def email_send(useremail, password):

    subject = "Trip - User Welcome Email"
    html_message = render_to_string('email.html', {'password': password})
    plain_message = strip_tags(html_message)
    from_email = 'Trip Techromatic <rpaideaplanner@gmail.com>'
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=from_email,
        to = [useremail, ],
        bcc= []

)
    email.content_subtype = "html"
    try:
        email.send(fail_silently=False)
    except:
        email_send(useremail, password)



def email_send_mfa(useremail, code):

    subject = "Trip - MFA Email"
    html_message = render_to_string('mfa.html', {'mfa_code': code})
    plain_message = strip_tags(html_message)
    from_email = 'Trip Techromatic <rpaideaplanner@gmail.com>'
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=from_email,
        to = [useremail, ],
        bcc= []

)
    email.content_subtype = "html"
    try:
        email.send(fail_silently=False)
    except:
        pass