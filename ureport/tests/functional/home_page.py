def home_page(driver):
    driver.open("/")
    assert driver.browser.is_text_present('0')
    assert driver.browser.is_text_present('HOME')
    assert driver.browser.is_text_present('POLL RESULTS')
    assert driver.browser.is_text_present('ABOUT UREPORT')
    assert driver.browser.is_text_present('HOW TO JOIN')
    assert driver.browser.is_text_present('PREVIOUS POLLS')


def home_page_visualisation( driver):
    driver.open('/')

    assert driver.browser.is_element_present_by_css('span.poll-question')
    assert driver.browser.is_element_present_by_css('div.highcharts-container')


def home_page_map(driver):
    driver.open('/')
    assert driver.browser.is_element_present_by_css('div#OpenLayers.Map_2_events')
    assert driver.browser.is_element_present_by_css('div#OpenLayers.Map_2_OpenLayers_ViewPort')


def best_viz(driver):
    driver.open('/bestviz/?pks=l')
    assert driver.browser.is_text_present('CURRENT POLL')












