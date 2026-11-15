import os

import pytest
from playwright.sync_api import expect

pytest_plugins = ["fixtures.pages_fixture"]

IS_CI = bool(os.getenv("CI"))

expect.set_options(timeout=15_000)


@pytest.fixture(scope="session", autouse=True)
def set_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Analogue of forbidOnly: a committed @pytest.mark.only fails CI."""
    if not IS_CI:
        return
    focused = [i.nodeid for i in items if i.get_closest_marker("only")]
    if focused:
        raise pytest.UsageError(
            f"@pytest.mark.only is forbidden in CI: {focused}"
        )