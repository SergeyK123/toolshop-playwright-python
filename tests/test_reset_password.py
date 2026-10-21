from playwright.sync_api import expect


def test_known_email_gets_confirmation(forgot_password_page):
    forgot_password_page.open()
    forgot_password_page.request_reset("customer@practicesoftwaretesting.com")

    expect(forgot_password_page.success_message).to_be_visible()
    expect(forgot_password_page.email_error).to_have_count(0)


def test_empty_email_shows_error(forgot_password_page):
    forgot_password_page.open()
    forgot_password_page.request_reset("")

    expect(forgot_password_page.email_error).to_be_visible()
    expect(forgot_password_page.success_message).not_to_be_visible()