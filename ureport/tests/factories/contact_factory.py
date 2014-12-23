import factory
import datetime

from rapidsms.models import Contact
from rapidsms_ureport.ureport.tests.factories.location_factory import LocationFactory


class ContactFactory(factory.DjangoModelFactory):
    class Meta:
        model = Contact

    reporting_location = factory.SubFactory(LocationFactory)