import re

from five import grok
from plone.directives import form
from zope.interface import Interface
from zope.interface import Invalid
from zope import schema
from z3c.form import field, button
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from tdf.templatesiteaccountform import _

from zope.schema.interfaces import Bool

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form.browser.radio import RadioFieldWidget

from zope.component import getMultiAdapter
from Acquisition import aq_inner
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget


class ReCaptcha(object):
    subject = u""
    captcha = u""
    def __init__(self, context):
        self.context = context


checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match

def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True



MESSAGE_TEMPLATE = """\

Account Request from %(firstname)s  %(name)s <%(emailAddress)s> for LibreOffice Templates site

Firstname: %(firstname)s
Name: %(name)s
Email: %(emailAddress)s
Prefered Username: %(preferedusername)s



%(message)s
"""



class ITemplateaccountForm(Interface):
    """Define the fields of our form
    """



    requestofaccount= schema.Text(
        title =_(u"Request for an account on the LibreOffice Templates Site: http://templates.libreoffice.org"),
        description=_(u"(If you created a template for LibreOffice and want to publish it on the LibreOffice Templates Site you could ask for an account on the site. Please tell us in the field below a bit about your template project.)"),
        readonly=True,
        required=False,
        )

    name = schema.TextLine(
        title=_(u"Lastname"),
        )


    firstname = schema.TextLine(
        title=_(u"Firstname"),
        )

    preferedusername = schema.ASCIILine(
        title=_(u"User Name (5 - 15 ASCII characters)"),
        description=_(u"If we should create a special user name please write it down. In case your preferred username is already taken we will add numbers to your suggestion. "),
        min_length=5,
        max_length=15,
        required=False,
        )



    emailAddress = schema.ASCIILine(
        title=_(u"Your email address (tied to your account)"),
        constraint=validateEmail
    )




    message = schema.Text(
        title=_(u"Short Description of Your Template Project"),
        description=_(u"Please keep to 1,000 characters"),
        max_length=1000,
        required=False,
        )

    captcha = schema.TextLine(
        title=_(u"ReCaptcha"),
        description=_(u""),
        required=False
    )

class TemplatesiteaccountForm(form.Form):


    grok.context(ISiteRoot)
    grok.name('ask-for-an-templatesiteaccount')
    grok.require('zope2.View')

    fields = field.Fields(ITemplateaccountForm)
    fields['captcha'].widgetFactory = ReCaptchaFieldWidget

    label = _(u"Ask for an Account")
    description = _(u"Please give us a short description of your template project.")

    ignoreContext = True


    # Hide the editable border and tabs
    def update(self):
        self.request.set('disable_border', True)
        return super(TemplatesiteaccountForm, self).update()

    @button.buttonAndHandler(_(u"Send"))
    def sendMail(self, action):
        """Send the email to the site administrator and redirect to the
        front page, showing a status message to say the message was received.
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            captcha = getMultiAdapter((aq_inner(self.context), self.request), name='recaptcha')
            if captcha.verify():
                print 'ReCaptcha validation passed.'
            else:
                print 'The code you entered was wrong, please enter the new one.'
            return

        mailhost = getToolByName(self.context, 'MailHost')
        urltool = getToolByName(self.context, 'portal_url')

        portal = urltool.getPortalObject()

        # Construct and send a message
        toAddress = portal.getProperty('email_from_address')
        source = "%s <%s>" % ('Asking for an Account on the template site', 'templates@otrs.documentfoundation.org')
        subject = "%s %s" % (data['firstname'], data['name'])
        message = MESSAGE_TEMPLATE % data

        mailhost.send(message, mto=toAddress, mfrom=str(source), subject=subject, charset='utf8')

        # Issue a status message
        confirm = _(u"Thank you! Your request for an account has been received and we will create an account. You will get an email with a link to activate your account and reset the password.")
        IStatusMessage(self.request).add(confirm, type='info')

        # Redirect to the portal front page. Return an empty string as the
        # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return ''

    @button.buttonAndHandler(_(u"Cancel"))
    def cancelForm(self, action):

        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()

        # Redirect to the portal front page. Return an empty string as the
        # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return u''


