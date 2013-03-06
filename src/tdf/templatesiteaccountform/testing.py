from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class TdftemplatesiteaccountformLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import tdf.templatesiteaccountform
        xmlconfig.file(
            'configure.zcml',
            tdf.templatesiteaccountform,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'tdf.templatesiteaccountform:default')

TDF_TEMPLATESITEACCOUNTFORM_FIXTURE = TdftemplatesiteaccountformLayer()
TDF_TEMPLATESITEACCOUNTFORM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TDF_TEMPLATESITEACCOUNTFORM_FIXTURE,),
    name="TdftemplatesiteaccountformLayer:Integration"
)
