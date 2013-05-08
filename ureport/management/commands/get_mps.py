from optparse import make_option
from django.core.management import BaseCommand
from message_classifier.models import IbmMsgCategory, IbmCategory
from rapidsms.contrib.locations.models import Location


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="path"),
    )

    def handle(self, **options):
        path = options.get('path')
        ibm = IbmMsgCategory.objects.filter(score__gte=0.5, msg__direction='I', msg__connection__contact__reporting_location__type__name='district').exclude(
            msg__connection__contact__reporting_location=None)
        locations = set(list(ibm.values_list("msg__connection__contact__reporting_location", flat=True).distinct()))

        print "District", " ".join([v.replace(" ", "_").replace("&", "and") for v in list(IbmCategory.objects.values_list('name', flat=True))])
        for location in locations:
            for_dist = {}
            for category in IbmCategory.objects.order_by('name'):
                for_dist[category.name] = ibm.filter(msg__connection__contact__reporting_location=location,
                                                     category=category).count()

            print Location.objects.get(pk=location).name, " ".join([str(v) for v in for_dist.values()]), 0