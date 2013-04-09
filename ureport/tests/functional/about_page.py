def about_ureport_page(driver):
    driver.browser.visit(driver.live_server_url + '/about_ureport/')
    assert driver.browser.is_text_present('About Ureport')