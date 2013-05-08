import json
from django.core.management import BaseCommand
from django.db.models.aggregates import Count
from message_classifier.models import IbmCategory
from rapidsms.contrib.locations.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        l = [l.pk for l in Location.objects.filter(type='district').distinct()]

        s = IbmCategory.objects.filter(ibmmsgcategory__score__gte=0.5,
                                       ibmmsgcategory__msg__connection__contact__reporting_location__in=l).annotate(
            total=Count('ibmmsgcategory')).values('total', 'name',
                                                  'ibmmsgcategory__msg__connection__contact__reporting_location__name').\
            exclude(name__in=['family & relationships', "energy", "u-report", "social policy", "employment"])

        data = json.dumps(list(s))
        print data