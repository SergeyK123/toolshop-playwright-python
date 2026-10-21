# Description

## What I want to do

Automate the five core user flows of the Toolshop (https://practicesoftwaretesting.com)
with Playwright and Python, following the SIS 2 brief of the course:

* five independent test cases, one spec file per case;
* Page Object Model: one class per screen, no locators in the spec files;
* at least one fixture (page objects, a registered user, a session login);
* a data factory, because registration needs a unique e-mail on every run;
* assertions that can really fail, no `waitForTimeout`/`sleep`, no CSS-class locators;
* tests that pass in any order and in parallel.

I used an AI assistant (Claude) to draft the structure and the code, and then I checked
every part against the real site, ran the suite many times and corrected what was wrong.
The prompts are in [Prompt.md](Prompt.md), the review and the corrections are in
[Review.md](Review.md).



## Technology

Python, pytest, pytest-playwright (Chromium), pytest-xdist (parallel run),
pytest-randomly (random test order), pytest-rerunfailures (only for CI use), Faker.
Locators use the `data-test` attribute (`testIdAttribute` equivalent configured in
`conftest.py`).

## List of test cases to be automated

| ID | Test case | What it must prove | Spec file | Tests |
|----|-----------|--------------------|-----------|-------|
| TC-01 | Register a new customer | A unique new account is created and the user lands on the login page; the new credentials really work; an already used e-mail is not accepted | `tests/test_register.py` | `test_new_customer_can_register_and_log_in`, `test_registration_with_existing_email_is_rejected` |
| TC-02 | Log in | Valid credentials reach `/account` and show the user name; invalid credentials show the error and do not open the account | `tests/test_login.py` | `test_valid_credentials_open_account_page`, `test_invalid_credentials_show_error` |
| TC-03 | Buy a product | After adding a product the cart shows the right name, quantity 1, line price and total; checkout (address, cash on delivery) ends with the success message | `tests/test_buy_product.py` | `test_logged_in_customer_buys_a_product` |
| TC-04 | Compare two products | Two different products are opened, name and price are captured, and the stated comparison (the hammer is cheaper than the pliers) is asserted | `tests/test_compare_products.py` | `test_two_products_can_be_compared_by_price` |
| TC-05 | Reset a password | A known e-mail gives the confirmation message and no error; an empty e-mail gives a validation error and no confirmation | `tests/test_reset_password.py` | `test_known_email_gets_confirmation`, `test_empty_email_shows_error` |

Total: 5 test cases, 5 spec files, 8 tests.

### Steps and checks of each case

**TC-01 Register.** Open the registration form, fill every field with generated data
(unique e-mail, random password, country KZ, date of birth 1995-05-15), submit.
Check: URL is `/auth/login`. Then sign in with the same e-mail and password.
Check: URL is `/account`. Negative: register with the e-mail of the seeded customer.
Check: the user stays on `/auth/register` and the form is still shown.

**TC-02 Log in.** Valid: sign in with the user registered by the suite.
Check: URL `/account`, page title contains "my account", the menu shows the user's first
name. Invalid: sign in with an e-mail that is not registered anywhere and a wrong
password. Check: the login error element is visible and the URL is not `/account`.

**TC-03 Buy a product.** Signed-in user: search "Bolt Cutters", open the product, read its
name and price, add it to the cart, open the cart. Checks: the cart row contains the
product name, quantity is 1, line price and cart total contain the product price.
Proceed, fill the billing address (Italy, 30100), choose "cash on delivery", confirm.
Check: the payment success message is visible.

**TC-04 Compare.** Search and open "Pliers" and read name and price; do the same for
"Hammer". Checks: both names contain the searched word, the names differ, both prices are
greater than zero, the cheaper product is the hammer and its price is lower than the price
of the pliers.

**TC-05 Reset password.** Open the login page, follow "Forgot your Password?". Known
e-mail: the confirmation text is visible and the e-mail error is not shown. Empty e-mail:
the e-mail error is visible and the confirmation is not shown.

## Test data

* A new user (unique e-mail, random password) is generated for every run by
  `data/user_factory.py`; the suite registers it once per session.
* One fixed billing address (Italy, 30100, house number 9) is used for the checkout;
  this combination was accepted by the site in a manual run.
* The seeded customer `customer@practicesoftwaretesting.com` is used only where no
  password is typed (duplicate e-mail check, reset password). Typing wrong passwords for
  a shared account locked it during development.

## Not automated and why

* Card payment: strict formats of the card fields; one payment method is enough for TC-03.
* The reset-password e-mail: it cannot be read on the hosted site, so TC-05 checks only
  what the page shows.
* Sign-in with Google: an external service.
* Favourites, filters, sorting, cart editing, profile editing: outside the five cases of
  the brief.

## How the brief is covered

| Requirement of the brief | Where |
|---|---|
| Five tests, one spec per case | `tests/` |
| Page objects used by the specs, no locator in a spec | `pages/`, checked with `grep` (empty result) |
| At least one fixture | `fixtures/pages_fixture.py` |
| Unique data where required | `data/user_factory.py` |
| Every test has an assertion that can fail | all specs use `expect(...)` or `assert` |
| No `waitForTimeout` / `sleep` | checked with `grep` (empty result) |
| Any order and parallel | `pytest-randomly`, `pytest -n 4` (see Review.md, section 5) |
| Run from a clean clone | see README.md |
| Description, Prompt, Review, screenshots, repository link | this repository |
