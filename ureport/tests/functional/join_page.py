from splinter import Browser
from ureport.tests.functional.splinter_wrapper import SplinterWrapper


def join_page( driver):
    driver.open('/join/')
    assert driver.browser.is_text_present('Ureport')
    assert driver.browser.is_text_present('How To Join')