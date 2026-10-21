import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.name = page.get_by_test_id("product-name")
        self.price = page.get_by_test_id("unit-price")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")
        self.cart_icon = page.get_by_test_id("nav-cart")
        self.search_input = page.get_by_test_id("search-query")
        self.search_submit = page.get_by_test_id("search-submit")

    def open_catalog(self):
        self.page.goto("/")

    def search(self, term: str):
        self.search_input.fill(term)
        self.search_submit.click()

    def open_by_name(self, product_name: str):
        self.page.get_by_role("link", name=product_name).first.click()

    def read_details(self) -> dict:
        expect(self.name).to_be_visible()
        expect(self.price).to_be_visible()
        name = self.name.inner_text().strip()
        price = float(re.sub(r"[^0-9.]", "", self.price.inner_text()))
        return {"name": name, "price": price}

    def add_current_to_cart(self):
        expect(
            self.add_to_cart_button,
            "Add to cart is disabled (product unavailable or the page is still loading)",
        ).to_be_enabled()
        self.add_to_cart_button.click()
        expect(self.cart_icon).to_contain_text("1")

    def open_cart(self):
        self.cart_icon.click()
        expect(self.page).to_have_url(re.compile(r"/checkout"))