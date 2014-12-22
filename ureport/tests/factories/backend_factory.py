import factory
from rapidsms.models import Backend


class BackendFactory(factory.DjangoModelFactory):
    class Meta:
        model = Backend

    name = factory.Sequence(lambda n: "backend {0}".format(n))

