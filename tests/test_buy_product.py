from playwright.sync_api import expect

from data.user_factory import BILLING_ADDRESS

PRODUCT = "Bolt Cutters"   


def test_logged_in_customer_buys_a_product(auth_product_page, auth_cart_page, auth_checkout_page):
    auth_product_page.open_catalog()
    auth_product_page.search(PRODUCT)
    auth_product_page.open_by_name(PRODUCT)

    details = auth_product_page.read_details()
    auth_product_page.add_current_to_cart()
    auth_product_page.open_cart()
    auth_cart_page.wait_until_loaded()

    expect(auth_cart_page.product_title).to_contain_text(details["name"])
    expect(auth_cart_page.quantity).to_have_value("1")
    expect(auth_cart_page.line_price).to_contain_text(f"{details['price']:.2f}")
    expect(auth_cart_page.cart_total).to_contain_text(f"{details['price']:.2f}")

    auth_cart_page.continue_to_checkout()
    auth_checkout_page.continue_as_logged_in()
    auth_checkout_page.fill_billing_address(BILLING_ADDRESS)
    auth_checkout_page.pay_cash_on_delivery()

    expect(auth_checkout_page.success_message).to_be_visible()