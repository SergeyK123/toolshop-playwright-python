from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.product_title = page.get_by_test_id("product-title")
        self.quantity = page.get_by_test_id("product-quantity")
        self.product_price = page.get_by_test_id("product-price")
        self.line_price = page.get_by_test_id("line-price")
        self.cart_total = page.get_by_test_id("cart-total")
        self.continue_shopping = page.get_by_test_id("continue-shopping")
        self.proceed = page.get_by_test_id("proceed-1")

    def wait_until_loaded(self):
        
        expect(self.product_title.first).to_be_visible()

    def continue_to_checkout(self):
        self.proceed.click()