import datetime
import factory
from django.contrib.auth.models import User


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    first_name = "first name"
    last_name = "last name"
    email = factory.Sequence(lambda n: 'user{0}@gmail.com'.format(n))
    is_staff = True
    date_joined = datetime.datetime.now()
