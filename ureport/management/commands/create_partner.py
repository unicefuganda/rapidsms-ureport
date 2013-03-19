from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand
from uganda_common.models import Access, AccessUrls

__author__ = 'kenneth'


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(username='RCO')
        user.set_password('ureportpartner')
        user.save()
        print "RCO Created"
        group = Group.objects.get(name='UNITED NATIONS ALL STAFF')
        print "Group", group, "gotten"
        user.groups.add(group)
        print "RCO added to group", group
        access = Access.objects.create(user=user)
        print "Access", access, "created"
        access.groups.add(group)
        print "Group", group, "added to ", access
        urls = [AccessUrls.objects.get_or_create(url=url)[0] for url in
                ['^alerts/$', '^mypolls/$', '^reporter/$', '^bestviz/$', '^bestviz/(?P<poll_id>\d+)/$',
                 '^pollresults/$', '^polls/', '^geoserver/']]
        for u in urls:
            access.allowed_urls.add(u)
            print "Resource", u, "added to", access
