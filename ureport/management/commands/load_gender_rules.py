from django.core.management import BaseCommand
import yaml
from  poll.models import Category
from ureport_project.rapidsms_polls.poll.models import Rule


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            print("usage: python manage.py load_gender_rules gender_rules.yaml")
            exit(-1)
        stream = open(args[0], 'r')
        data = yaml.load(stream)
        categories = data['rules']
        for category_name, category_rules in categories.iteritems():
            category_in_db, created = Category.objects.get_or_create(name=category_name)
            languages = category_rules.keys()
            for language in languages:
                rule_string = ",".join(category_rules[language])
                created=category_in_db.rules.create(rule_string=rule_string,rule_type=Rule.TYPE_CONTAINS,regex=rule_string,rule=Rule.contains_one_of)




