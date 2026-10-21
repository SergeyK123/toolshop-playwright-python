import re

from playwright.sync_api import Page, expect


def test_valid_credentials_open_account_page(login_page, registered_user, page: Page):
    login_page.open()
    login_page.sign_in(registered_user.email, registered_user.password)

    expect(page).to_have_url(re.compile(r"/account"))
    expect(login_page.account_title).to_contain_text(re.compile("my account", re.I))
    expect(login_page.nav_menu).to_contain_text(registered_user.first_name)


def test_invalid_credentials_show_error(login_page, new_user, page: Page):
    
    login_page.open()
    login_page.sign_in(new_user.email, "WrongPassword!1")

    expect(login_page.error_message).to_be_visible()
    expect(page).not_to_have_url(re.compile(r"/account"))