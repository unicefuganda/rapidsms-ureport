import time

def fill_form(browser, field_values, by_name=False, select_by_value=False):
    time.sleep(5)
    for id, value in field_values.items():
        if by_name:
            elements = browser.find_by_name(id)
        else:
            elements = browser.find_by_id(id)
        element = elements.first
        if element['type'] == 'text' or element.tag_name == 'textarea' or element['type'] == 'password':
            element.value = value
        elif element['type'] == 'checkbox':
            if value:
                element.check()
            else:
                element.uncheck()
        elif element['type'] == 'radio':
            for field in elements:
                if field.value == value:
                    field.click()
        elif element._element.tag_name == 'select':
            if select_by_value:
                element.find_by_value(value).first._element.click()
            else:
                element.find_by_xpath('.//*[contains(., "%s")]' % value).first._element.click()

        assert element is not None

def fill_form_and_submit(browser, form_data, submit_button_name, by_name=False, select_by_value=False):
    fill_form(browser, form_data, by_name, select_by_value)
    is_submit_present = browser.is_element_present_by_name(submit_button_name)
    assert is_submit_present is True
    browser.find_by_name(submit_button_name).first.click()


def rows_of_table_by_class(browser, container_class):
    return browser.find_by_xpath('//*[@class="%s"]/table/tbody/tr' % container_class)
