def login_fails_without_user(driver):
    driver.open('/accounts/login')
    driver.browser.fill("username", "a")
    driver.browser.fill("password", "a")
    driver.browser.find_by_css("input[type=submit]").first.click()
    assert driver.browser.is_text_present('Oops. Your username and password didn\'t match. Please try again.')


def login_succeeds_with_super_user(driver):
    user = driver.create_and_sign_in_admin("pass", "jamo")
    assert driver.browser.is_text_present('POLL ADMIN')
    assert driver.browser.is_text_present('MESSAGE LOG')
    assert driver.browser.is_text_present('MESSAGE CLASSIFICATION')
    assert driver.browser.is_text_present('UREPORTERS')
    assert driver.browser.is_text_present('FLAGGED MESSAGES')
    assert driver.browser.is_text_present('Real Time')