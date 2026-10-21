import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.nav_sign_in = page.get_by_test_id("nav-sign-in")
        self.email = page.get_by_test_id("email")
        self.password = page.get_by_test_id("password")
        self.submit = page.get_by_test_id("login-submit")
        self.error_message = page.get_by_test_id("login-error")
        self.account_title = page.get_by_test_id("page-title")
        self.nav_menu = page.get_by_test_id("nav-menu")

    def open(self):
        
        self.page.goto("/")
        self.nav_sign_in.click()
        expect(self.page).to_have_url(re.compile(r"/auth/login"))

    def sign_in(self, email: str, password: str):
        self.email.fill(email)
        self.password.fill(password)
        self.submit.click()