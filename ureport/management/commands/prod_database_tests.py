from django.core.management.base import NoArgsCommand
import unittest

class Command(NoArgsCommand):
    help = """
     This are database based tests for stress testing and making sure view response times are within
     normal params
    """

    def handle_noargs(self, **options):
        suite = unittest.TestLoader().loadTestsFromTestCase(LiveTest)
        unittest.TextTestRunner().run(suite)


class LiveTest(unittest.TestCase):
    def setUp(self):
        print ""

    def test_equality(self):
        """
        Tests that 1 + 1 always equals 2.
        """

        self.failUnlessEqual(1 + 1, 2)