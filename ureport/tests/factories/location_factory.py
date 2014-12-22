import factory
from rapidsms.contrib.locations.models import Location


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location
