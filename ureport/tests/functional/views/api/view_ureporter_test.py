from django.test import TestCase


class ViewUreporterTestCase(TestCase):
    def test_view_ureporter_api_url(self):
        response = self.client.get("/ureporters/console/999")
        self.assertEqual(200,response.status_code)
