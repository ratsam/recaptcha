from django.template.loader import render_to_string
from django.template.context import Context
from django.utils.safestring import mark_safe
from django.conf import settings
import urllib2, urllib

API_SSL_SERVER = "https://api-secure.recaptcha.net"
API_SERVER = "http://api.recaptcha.net"
VERIFY_SERVER = "api-verify.recaptcha.net"

# customization (first value is used as fallback)
VALID_THEMES = ('red', 'white', 'blackglass', 'clean', 'custom')
VALID_LANGS = ('en', 'nl', 'fr', 'de', 'pt', 'ru', 'es', 'tr')

if 'recaptcha' not in settings.INSTALLED_APPS:
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    try:
        get_template('recaptcha/custom.html')
    except TemplateDoesNotExist:
        from warnings import warn
        warn('If you are using custom reCAPTCHA theme, please insert \'recaptcha\' in your INSTALLED_APPS or \n copy \'custom.html\' to TEMPLATE_DIRS + \'recaptcha/\'')

class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code

def displayhtml (public_key, use_ssl=False, error=None,
                 theme='red',lang='en', tabindex=0,
                 custom_theme_widget='recaptcha_custom_widget',
                 template_name='recaptcha/custom.html'):
    """Gets the HTML to display for reCAPTCHA

    public_key -- The public api key
    use_ssl -- Should the request be sent over ssl?
    error -- An error message to display (from RecaptchaResponse.error_code)
    theme -- Color Theme
    lang -- Language Code
    tabindex -- Tabindex to use for the field
    custom_theme_widge -- Custom theme widget (A string with the ID of a DOM element)
    
    More info: http://recaptcha.net/apidocs/captcha/client.html
    """

    error_param = ''
    if error:
        error_param = '&error=%s' % error

    if use_ssl:
        server = API_SSL_SERVER
    else:
        server = API_SERVER

    theme = (VALID_THEMES[0], theme) [ theme in VALID_THEMES ]
    lang = (VALID_LANGS[0], lang) [ lang in VALID_LANGS ]
    
    html = u"""<script type="text/javascript">
                  var RecaptchaOptions={
                      theme:'%(theme)s',
                      lang:'%(lang)s',
                      tabindex:'%(tabindex)s',
                      custom_theme_widget:'%(custom_theme_widget)s'
                  };
                </script>

                <script type="text/javascript" src="%(ApiServer)s/challenge?k=%(PublicKey)s%(ErrorParam)s"></script>
                <noscript>
                   <iframe src="%(ApiServer)s/noscript?k=%(PublicKey)s%(ErrorParam)s" height="300" width="500" frameborder="0"></iframe><br/>
                   <textarea name="recaptcha_challenge_field" rows="3" cols="40">
                   </textarea>
                   <input type="hidden" name="recaptcha_response_field" value="manual_challenge"/>
                </noscript>
            """ % {
                'ApiServer'          : server,
                'PublicKey'          : public_key,
                'ErrorParam'         : error_param,
                'theme'              : theme,
                'lang'               : lang,
                'tabindex'           : tabindex,
                'custom_theme_widget': custom_theme_widget }
    
    if theme == 'custom':
        html = mark_safe(html)
        html = render_to_string(template_name, context_instance=Context({'rendered_scripts':html}))
    return html

def submit (recaptcha_challenge_field,
            recaptcha_response_field,
            private_key,
            remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from the form
    recaptcha_response_field -- The value of recaptcha_response_field from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
        return RecaptchaResponse (is_valid = False, error_code = 'incorrect-captcha-sol')
    
    params = urllib.urlencode ({
        'privatekey': private_key,
        'remoteip'  : remoteip,
        'challenge' : recaptcha_challenge_field,
        'response'  : recaptcha_response_field.encode('utf-8'),
        })

    request = urllib2.Request (
        url = "http://%s/verify" % VERIFY_SERVER,
        data = params,
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
            }
        )
    
    httpresp = urllib2.urlopen (request)

    return_values = httpresp.read ().splitlines ();
    httpresp.close();

    return_code = return_values [0]
    if (return_code == "true"):
        return RecaptchaResponse (is_valid=True)
    else:
        return RecaptchaResponse (is_valid=False, error_code = return_values [1])


