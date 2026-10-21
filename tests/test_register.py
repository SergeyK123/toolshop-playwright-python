import re

from playwright.sync_api import Page, expect

from data.user_factory import SEEDED_CUSTOMER


def test_new_customer_can_register_and_log_in(register_page, login_page, new_user, page: Page):
    register_page.open()
    register_page.register(new_user)

    
    expect(page).to_have_url(re.compile(r"/auth/login"))

    
    login_page.sign_in(new_user.email, new_user.password)
    expect(page).to_have_url(re.compile(r"/account"))


def test_registration_with_existing_email_is_rejected(register_page, new_user, page: Page):
    new_user.email = SEEDED_CUSTOMER["email"]
    register_page.open()
    register_page.register(new_user)

    expect(page).to_have_url(re.compile(r"/auth/register"))
    expect(register_page.submit).to_be_visible()