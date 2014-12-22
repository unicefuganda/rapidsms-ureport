import datetime
import factory
from rapidsms_polls.poll.models import Poll
from rapidsms_ureport.ureport.tests.factories.user_factory import UserFactory


class PollFactory(factory.DjangoModelFactory):
    class Meta:
        model = Poll

    name = "Poll Name"
    question = "Poll Question"
    user = factory.SubFactory(UserFactory)
    start_date = datetime.datetime.today()
    end_date = datetime.datetime.today() + datetime.timedelta(days=1)
    type = 't'
    default_response = 'Ok'
    response_type = 'a'

    @factory.post_generation
    def messages(self, create, extracted, **_):
        if not create:
            return

        if extracted:
            for message in extracted:
                self.messages.add(message)

    @factory.post_generation
    def contacts(self, create, extracted, **_):
        if not create:
            return

        if extracted:
            for contact in extracted:
                self.contacts.add(contact)

    @factory.post_generation
    def sites(self, create, extracted, **_):
        if not create:
            return

        if extracted:
            for site in extracted:
                self.sites.add(site)