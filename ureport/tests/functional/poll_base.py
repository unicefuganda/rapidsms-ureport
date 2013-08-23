from poll.models import Poll
from ureport.tests.functional.poll_assertions import PollAssertions
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure


class PollBase(PollAssertions):

    @take_screenshot_on_failure
    def start_poll(self):
        poll_url = "/view_poll/%s" % self.poll.id
        self.create_and_sign_in_admin("argha", "a", poll_url)

        assert self.browser.is_text_present('Start Poll',10)
        self.browser.find_link_by_text('Start Poll').first.click()

        assert self.browser.is_text_present('Close Poll')

    def get_poll(self, poll_id):
        return Poll.objects.get(id=poll_id)