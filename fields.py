from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from utils import obtain_request
from librecaptcha import displayhtml, submit

RECAPTCHA_LANG = getattr(settings, 'LANGUAGE_CODE', 'en')
RECAPTCHA_THEME = getattr(settings, 'RECAPTCHA_THEME', 'red')

ERROR_CODES = {
    "unknown" :    					_("Unknown error."),
    "invalid-site-public-key" :    	_("We weren't able to verify the public key. Please try again later."),
    "invalid-site-private-key" : 	_("We weren't able to verify the private key. Please try again later."),
    "invalid-request-cookie" : 		_("The challenge parameter of the verify script was incorrect."),
    "incorrect-captcha-sol" : 		_("The CAPTCHA solution was incorrect."),
    "verify-params-incorrect" : 	_("The parameters to /verify were incorrect, make sure you are passing all the required parameters.  Please try again later."),
    "invalid-referrer" : 			_("reCAPTCHA API keys are tied to a specific domain name for security reasons.  Please try again later."),
    "recaptcha-not-reachable" :    	_("Unable to contact the reCAPTCHA verify server.  Please try again later.")
}

class RecaptchaWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        html = displayhtml(settings.RECAPTCHA_PUBLIC_KEY,
                           theme=RECAPTCHA_THEME,
                           lang=RECAPTCHA_LANG)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        challenge = data.get('recaptcha_challenge_field')
        response = data.get('recaptcha_response_field')
        return (challenge, response)

    def id_for_label(self, id_):
        return None


class RecaptchaField(forms.Field):
    widget = RecaptchaWidget

    def clean(self, value):
        challenge, response = super(RecaptchaField, self).clean(value)
        
        if not challenge:
            raise forms.ValidationError(_('An error occured with the CAPTCHA service. Please try again.'))
        if not response:
            raise forms.ValidationError(_('Please enter the CAPTCHA solution.'))
        
        remote_ip = obtain_request().META['REMOTE_ADDR'];
        
        rc = submit(challenge, response, settings.RECAPTCHA_PRIVATE_KEY, remote_ip)
        if not rc.is_valid:
            msg = ERROR_CODES.get(rc.error_code, ERROR_CODES['unknown'])
            raise forms.ValidationError(msg)
       
        return True

