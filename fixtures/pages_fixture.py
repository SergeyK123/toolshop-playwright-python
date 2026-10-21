import re

import pytest
from playwright.sync_api import expect

from data.user_factory import create_user
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.forgot_password_page import ForgotPasswordPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.register_page import RegisterPage



@pytest.fixture(scope="session")
def registered_user(browser, base_url):
    
    user = create_user()
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    register = RegisterPage(page)
    register.open()
    register.register(user)
    expect(page).to_have_url(re.compile(r"/auth/login"))
    context.close()
    return user



@pytest.fixture(scope="session")
def auth_state(browser, base_url, registered_user, tmp_path_factory):
    path = tmp_path_factory.mktemp("auth") / "user.json"
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    login = LoginPage(page)
    login.open()
    login.sign_in(registered_user.email, registered_user.password)
    expect(page).to_have_url(re.compile(r"/account"))
    context.storage_state(path=str(path))
    context.close()
    return str(path)


@pytest.fixture
def auth_page(new_context, auth_state):
    
    context = new_context(storage_state=auth_state)
    return context.new_page()



@pytest.fixture
def new_user():
    return create_user()



@pytest.fixture
def login_page(page):
    return LoginPage(page)


@pytest.fixture
def register_page(page):
    return RegisterPage(page)


@pytest.fixture
def product_page(page):
    return ProductPage(page)


@pytest.fixture
def forgot_password_page(page):
    return ForgotPasswordPage(page)



@pytest.fixture
def auth_product_page(auth_page):
    return ProductPage(auth_page)


@pytest.fixture
def auth_cart_page(auth_page):
    return CartPage(auth_page)


@pytest.fixture
def auth_checkout_page(auth_page):
    return CheckoutPage(auth_page)