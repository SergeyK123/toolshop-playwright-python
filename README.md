# Toolshop Playwright tests (Python)

Automated UI tests for the Toolshop, https://practicesoftwaretesting.com, written with
Playwright (Python) and pytest. This is the SIS 2 assignment of the course
"Software Testing and Debugging" (Test Automation with Playwright).

* 5 test cases, 5 spec files, 8 tests in total
* Page Object Model, custom fixtures, unique test data generated on every run
* No fixed sleeps and no locators in the spec files

Other documents in this repository: [Description.md](Description.md) (what is automated),
[Prompt.md](Prompt.md) (the prompts sent to the AI tool), [Review.md](Review.md)
(what the AI produced, how I reviewed and changed it, why).

## Requirements

* Python 3.10 or newer (developed and tested on Python 3.14, macOS)
* Git
* Internet access (the tests run against the public site)

## Setup

```bash
git clone <https://github.com/SergeyK123/toolshop-playwright-python>
cd toolshop-playwright-python

python3 -m venv tollshop-playwright-testing.venv
source tollshop-playwright-testing.venv/bin/activate            

pip install -r requirements.txt
playwright install chromium
```

Equivalent of the commands of the course brief (the project is written in Python, not in
JavaScript):

| Brief | This project |
|---|---|
| `git clone ...` | `git clone <repository-url>` |
| `npm install` | `pip install -r requirements.txt` (inside the virtual environment) |
| `npx playwright install` | `playwright install chromium` |
| `npx playwright test` | `python -m pytest` |

Always run the tests from the project root with the virtual environment active.
`python -m pytest` is used on purpose: it guarantees that the pytest of the virtual
environment is used (a different pytest, for example from Anaconda, does not find the
project modules).

## Run

| Goal | Command |
|---|---|
| All tests | `python -m pytest` |
| Parallel (4 workers) | `python -m pytest -n 4` |
| One file | `python -m pytest tests/test_login.py -v` |
| One test by name | `python -m pytest -k invalid_credentials -v` |
| Visible browser | `python -m pytest --headed` |
| Visible and slow | `python -m pytest --headed --slowmo 500` |
| Fixed test order | `python -m pytest -p no:randomly` |
| Repeat a random order | `python -m pytest --randomly-seed=12345` (number from the header `Using --randomly-seed=...`) |
| Against the buggy build | `python -m pytest --base-url=https://with-bugs.practicesoftwaretesting.com` |
| Always save a trace | `python -m pytest --tracing on` |
| Screenshot of every test (evidence of a run) | `python -m pytest --screenshot on --output=screenshots/run-results` |

Tests run in random order (pytest-randomly) and are independent, so they can also run in
parallel. On a failure a screenshot and a trace are saved to `test-results/`.
Open a trace with:

```bash
playwright show-trace test-results/<test-folder>/trace.zip
```

## Project structure

```
toolshop-playwright-python/
├── README.md  Description.md  Prompt.md  Review.md  BugReports.md
├── conftest.py            test id attribute (data-test) and default assertion timeout
├── pytest.ini             base URL and run options
├── requirements.txt
├── data/
│   └── user_factory.py    generates a unique user for every run
├── fixtures/
│   └── pages_fixture.py   page objects, registered user, session login (storage state)
├── pages/                 page objects, one class per screen (all locators live here)
│   ├── base_page.py  login_page.py  register_page.py  product_page.py
│   └── cart_page.py  checkout_page.py  forgot_password_page.py
├── tests/                 one spec file per test case, no locators inside
│   ├── test_register.py  test_login.py  test_buy_product.py
│   └── test_compare_products.py  test_reset_password.py
├── screenshots/           screenshots used in Review.md
└
└── buggy-run-2.txt    run against the buggy build, pages opened through the menu
```

## What is covered

| # | Test case | File | Tests |
|---|---|---|---|
| 1 | Register a new customer | `tests/test_register.py` | new user can register and then log in; an already used email is rejected |
| 2 | Log in | `tests/test_login.py` | valid credentials open the account page; invalid credentials show an error |
| 3 | Buy a product | `tests/test_buy_product.py` | add to cart, check the cart, checkout with cash on delivery, success message |
| 4 | Compare two products | `tests/test_compare_products.py` | capture name and price of two products, assert the stated price comparison |
| 5 | Reset a password | `tests/test_reset_password.py` | confirmation for a known email; error for an empty email |

## Design decisions

* **Own test user.** The suite registers its own user once per session and signs in with
  it. The shared seeded accounts are not used for typing passwords: other users of the
  public site can lock them (this happened during development, see Review.md).
* **Session login once.** The fixture `auth_state` signs in through the UI once and
  stores the session; tests that need a signed-in user reuse it. The login test itself
  always uses the UI.
* **Unique data.** The email and the password are generated with `uuid` for every run, so
  repeated and parallel runs do not collide.
* **Locators only in page objects.** Elements are found with `data-test` attributes
  (`get_by_test_id`), by role or by text when no test id exists.
* **No fixed sleeps.** The tests wait only through web-first assertions and explicit
  waits for a state. The default assertion timeout is 15 s because the public site can
  answer slowly.
* **Payment** is done with "cash on delivery". Card payment needs strict field formats
  and is not covered.

## Not covered

Card payment, sign-in with Google, the real reset-password e-mail (it cannot be read on
the hosted site), favourites, filters and sorting, profile editing.

## Known limitations

* The price comparison test depends on the current prices on the public site.
* The site is shared and can be slow or temporarily unavailable.
* The reset-password confirmation has no `data-test` attribute and shows the raw
  translation key `page.forgot-password.confirm`; the test finds it by this text.
* The suite is not free of flaky behaviour on the shared public site: a button of the shop
  (for example "Add to cart" or the billing step "Proceed") sometimes stays disabled
  longer than the test waits. See Review.md, problems 7, 10 and 11.
* The buggy build (`with-bugs.practicesoftwaretesting.com`) uses hash routes
  (`/#/auth/login`) and answers a direct link such as `/auth/login` with an Apache
  "404 Not Found". For this reason the page objects open pages through the menu. On that
  build four tests are blocked by the registration form (no field `postal_code`), see
  Review.md, section 6, and BugReports.md.
