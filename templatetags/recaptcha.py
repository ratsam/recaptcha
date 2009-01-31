from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from inetss.django.apps.recaptcha.librecaptcha import displayhtml

register = template.Library()

@register.tag
def recaptcha(parser, token):
    try:
        tag_name, theme, template_name = token.split_contents()
    except ValueError:
        try:
            tag_name, theme = token.split_contents()
            if theme == 'custom':
                raise template.TemplateSyntaxError, "%r tag requires template name if using custom theme" % tag_name
            return RecaptchaNode(theme)
        except ValueError:
            raise template.TemplateSyntaxError, "%r tag requires a theme as arguments" % token.contents.split()[0]
    
    return RecaptchaNode(theme, template_name)

class RecaptchaNode(template.Node):

    def __init__(self, theme, template_name='recaptcha/custom.html'):
        self.theme = theme
        self.template_name = template_name

    def render(self, context):
        return mark_safe(displayhtml(settings.RECAPTCHA_PUBLIC_KEY,
                                      theme=self.theme, lang=settings.LANGUAGE_CODE,
                                      template_name=self.template_name))
