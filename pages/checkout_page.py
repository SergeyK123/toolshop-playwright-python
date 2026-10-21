from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.proceed_from_login = page.get_by_test_id("proceed-2")
        self.proceed_from_address = page.get_by_test_id("proceed-3")
        self.country = page.get_by_test_id("country")
        self.state = page.get_by_test_id("state")
        self.postal_code = page.get_by_test_id("postal_code")
        self.house_number = page.get_by_test_id("house_number")
        self.street = page.get_by_test_id("street")
        self.city = page.get_by_test_id("city")
        self.payment_method = page.get_by_test_id("payment-method")
        self.confirm = page.get_by_test_id("finish")
        self.success_message = page.get_by_test_id("payment-success-message")

    def continue_as_logged_in(self):
        self.proceed_from_login.click()

    def fill_billing_address(self, address: dict):
        
        expect(
            self.street, "Billing form was not pre-filled in time"
        ).not_to_have_value("")

        self.country.select_option(address["country"])
        self.postal_code.fill(address["postal_code"])
        self.house_number.fill(address["house_number"])
        self.street.fill(address["street"])
        self.city.fill(address["city"])
        self.state.fill(address["state"])

        
        expect(self.country).to_have_value(address["country"])
        expect(self.postal_code).to_have_value(address["postal_code"])
        expect(self.house_number).to_have_value(address["house_number"])
        expect(self.street).to_have_value(address["street"])
        expect(self.city).to_have_value(address["city"])
        expect(self.state).to_have_value(address["state"])

        try:
            expect(self.proceed_from_address).to_be_enabled()
        except AssertionError as error:
            values = {
                "country": self.country.input_value(),
                "postal_code": self.postal_code.input_value(),
                "house_number": self.house_number.input_value(),
                "street": self.street.input_value(),
                "city": self.city.input_value(),
                "state": self.state.input_value(),
            }
            raise AssertionError(
                f"'Proceed' stays disabled, the billing form is not valid. Field values: {values}"
            ) from error
        self.proceed_from_address.click()

    def pay_cash_on_delivery(self):
        self.payment_method.select_option("cash-on-delivery")
        self.confirm.click()