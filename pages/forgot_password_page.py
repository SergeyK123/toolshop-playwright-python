import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ForgotPasswordPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.link_on_login = page.get_by_test_id("forgot-password-link")
        self.email = page.get_by_test_id("email")
        self.submit = page.get_by_test_id("forgot-password-submit")
        self.email_error = page.get_by_test_id("email-error")
        self.nav_sign_in = page.get_by_test_id("nav-sign-in")
        
        self.success_message = page.get_by_text("page.forgot-password.confirm")

    def open(self):
        self.page.goto("/")
        self.nav_sign_in.click()
        self.link_on_login.click()
        expect(self.page).to_have_url(re.compile(r"/auth/forgot-password"))

    def request_reset(self, email: str):
        self.email.fill(email)
        self.submit.click()