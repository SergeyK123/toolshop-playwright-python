import pytest
from playwright.sync_api import expect

pytest_plugins = ["fixtures.pages_fixture"]


expect.set_options(timeout=15_000)


@pytest.fixture(scope="session", autouse=True)
def set_test_id_attribute(playwright):
    
    playwright.selectors.set_test_id_attribute("data-test")