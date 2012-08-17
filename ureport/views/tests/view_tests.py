import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
class TestViews(TestCase):

    def setUp(self):
        pass
    def test_home(self):
        
        response = self.client.get(reverse('ureport-home'))
        self.assertEqual(response.status_code, 200)

    def test_reporter(self):
        
        response = self.client.get(reverse('survey_home'))
        self.assertEqual(response.status_code, 200)


    def test_poll_dashboard(self):
        
        response = self.client.get(reverse('poll_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        
        response = self.client.get(reverse('reporter-profile'))
        self.assertEqual(response.status_code, 200)

    def test_polls(self):
        
        response = self.client.get(reverse('ureport-polls'))
        self.assertEqual(response.status_code, 200)
    def test_scriptpolls(self):
        
        response = self.client.get(reverse('script-polls'))
        self.assertEqual(response.status_code, 200)
    def test_massmessages(self):
        
        response = self.client.get(reverse('massmessages'))
        self.assertEqual(response.status_code, 200)
    def test_messagelog(self):
        
        response = self.client.get(reverse('messagelog'))
        self.assertEqual(response.status_code, 200)
    def test_quitmessages(self):
        
        response = self.client.get(reverse('quitmessages'))
        self.assertEqual(response.status_code, 200)
    def test_flaggedmessages(self):
        
        response = self.client.get(reverse('flaggedmessages'))
        self.assertEqual(response.status_code, 200)
    def test_flaggedwith(self):
        
        response = self.client.get(reverse('flagged_with'))
        self.assertEqual(response.status_code, 200)
    def test_newflag(self):
        
        response = self.client.get(reverse('flags_new'))
        self.assertEqual(response.status_code, 200)






    def test_deleteflag(self):
        
        response = self.client.get(reverse('delete_flag'))
        self.assertEqual(response.status_code, 200)



    def test_poll_responses(self):
        
        response = self.client.get(reverse('responses'))
        self.assertEqual(response.status_code, 200)




    def test_ureportcontent(self):
        
        response = self.client.get(reverse('ureport_content'))
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        
        response = self.client.get(reverse('ureport-about'))
        self.assertEqual(response.status_code, 200)

    def test_stories(self):
        
        response = self.client.get(reverse('ureport-stories'))
        self.assertEqual(response.status_code, 200)

    def test_message_feed(self):
        
        response = self.client.get(reverse('message-feed'))
        self.assertEqual(response.status_code, 200)

    def test_pollresults(self):
        
        response = self.client.get(reverse('polls-summary'))
        self.assertEqual(response.status_code, 200)
        
    def test_bestviz(self):
        
        response = self.client.get(reverse('best-viz'))
        self.assertEqual(response.status_code, 200)

    def test_tagcloud(self):
        response = self.client.get(reverse('tagcloud'))
        self.assertEqual(response.status_code, 200)

    def test_histogram(self):
        response = self.client.get(reverse('histogram'))
        self.assertEqual(response.status_code, 200)

    def test_clickatel(self):
        response = self.client.get(reverse('clickatel'))
        self.assertEqual(response.status_code, 200)

    def test_timeseries(self):
        response = self.client.get(reverse('time-series'))
        self.assertEqual(response.status_code, 200)


    def test_signup(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_messaghistory(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
    def test_mpdashboard(self):
        response = self.client.get(reverse('mp_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_ussdmanager(self):
        response = self.client.get(reverse('ussd_manager'))
        self.assertEqual(response.status_code, 200)


    def test_viewpoll(self):
        response = self.client.get(reverse('view_poll'))
        self.assertEqual(response.status_code, 200)

    def test_sendmessage(self):
        response = self.client.get(reverse('send_message'))
        self.assertEqual(response.status_code, 200)

    def test_editcategory(self):
        response = self.client.get(reverse('edit_category'))
        self.assertEqual(response.status_code, 200)

    def test_grouprules(self):
        response = self.client.get(reverse('view_rules'))
        self.assertEqual(response.status_code, 200)

    def test_alerts(self):
        response = self.client.get(reverse('alerts'))
        self.assertEqual(response.status_code, 200)

    def test_viewcategory(self):
        response = self.client.get(reverse('view_category'))
        self.assertEqual(response.status_code, 200)


