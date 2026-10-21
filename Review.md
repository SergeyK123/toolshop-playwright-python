# Review

## 1. Tool and how I used it

I used Claude (Anthropic), model Claude Sonnet 5.5, in the claude.ai chat. 

### The first prompt

The first prompt was a role prompt (in Russian, as I wrote it). In English:

> You are a Senior QA Automation Engineer with more than 8 years of experience in test
> automation of web applications, specialising in Python, Playwright, pytest, REST API and
> building maintainable automated test systems. You have practical experience in organising
> regression testing, finding defects, analysing flaky tests and preparing projects for
> regular team use. Your task is to develop a working automated test system for the
> Toolshop web shop, meant to reduce manual QA work and to check the functionality of the
> application regularly. Object under test: https://practicesoftwaretesting.com/

The prompt names the application and the tools, but it does **not** contain the five test
cases, the Page Object rules or the rules of the SIS 2 brief. The AI therefore answered a
general task ("build a test system for the shop"), not the task of the brief. 

### What the first answer contained

* A **strategy** with three layers: API tests (~50 %, every PR), UI smoke (~15 %, every
  PR) and UI regression (~35 %, nightly). Principles: prepare data through the API and check
  it through the UI, independent tests that can run in parallel (`pytest-xdist`), login once
  through `storage_state`, only web-first assertions and no `sleep`, at most one retry and
  only for UI tests, a trace for every failed test.

* `requirements.txt`: `pytest 8.3`, `pytest-playwright 0.5`, `pytest-xdist 3.6`,
  `pytest-rerunfailures 14`, `pytest-html 4.1`, `requests 2.32`, `python-dotenv 1.0`.
* `pytest.ini` with `-n auto`, an HTML report, `--tracing=retain-on-failure`,
  `--screenshot=only-on-failure` and the markers `smoke`, `regression`, `api`, `ui`.
* A project structure `toolshop-tests/`: `.github/workflows/tests.yml`, `api/client.py`,
  `config/settings.py`, `pages/` (base, login, home, product, cart), `tests/api/`
  (auth, products), `tests/ui/` (login, catalog, cart), `conftest.py`, `.env.example`.

## 2. What the AI results were about

The first answer (above) was a framework outline. After I gave the AI the real brief
(five cases, one spec per case, Page Object rules, no `sleep`, any order and parallel), it
produced, step by step:

* an instruction for the whole task (environment, project structure, commands);
* the configuration (`pytest.ini`, `conftest.py` with the `data-test` attribute);
* a data factory for unique users;
* page objects for login, registration, product, cart, checkout and forgot-password;
* a fixtures module (page objects, a registered user, a login that is done once);
* five spec files with assertions (8 tests);
* the checks for the rules of the brief (`grep` for sleeps and locators in specs);
* an analysis of the failures that I pasted (wrong expectation, locked account, flaky
  steps, the 404 of the buggy host, the differences found on the buggy build).

### First answer compared with the final project

| Part of the first answer | In the final project | Reason |
|---|---|---|
| API tests (~50 % of the suite), `api/client.py`, `tests/api/` | not used | The brief asks for five UI cases, one spec per case. The final suite has UI tests only. |
| Layers smoke / regression, markers `smoke`, `regression`, `api`, `ui` | not used | There are only 8 UI tests of one level, so there is nothing to split into layers. |
| `tests/ui/test_login.py`, `test_catalog.py`, `test_cart.py` (by feature) | `tests/test_register.py`, `test_login.py`, `test_buy_product.py`, `test_compare_products.py`, `test_reset_password.py` (one file per case) | The brief: one spec file per test case. |
| `pages/`: base, login, home, product, cart | `pages/`: base, login, register, product, cart, checkout, forgot_password | The five cases need registration, checkout and password reset screens. There is no home page object: the flows open `/` and go on through the menu. |
| `config/settings.py`, `.env.example`, `python-dotenv` | base URL in `pytest.ini`, `--base-url` option | There is one URL and no secret. The URL is given by `--base-url`, so the run against the buggy build is one command (section 6). |
| `requests` | not used | No API calls in the suite. |
| `pytest-html`, report in `reports/report.html` | not used | Evidence of a run is the console output, the trace and the screenshots (`--tracing`, `--screenshot`, `--output`). |
| `pytest.ini`: `-n auto` in `addopts` | the default run is sequential, parallel is `-n 4` on request | The brief asks for both modes, so I run both on purpose and compare them (section 5). |
| `.github/workflows/tests.yml` (CI) | not added | Not required by the brief; listed in section 8. |
| `pytest-rerunfailures`, "no more than one retry" | installed, not used (no `--reruns` anywhere) | A retry would hide flaky behaviour (section 7). |
| `storage_state` login once | kept (`auth_state` fixture) | Correct and useful. |
| `data-test` selectors, web-first assertions, no `sleep`, independent tests | kept | Correct and required by the brief. |
| Data prepared through the API | not used; the user is registered through the UI once per session (`registered_user` fixture) | No API client in the suite. The registration form is test case TC-01 anyway. |
| (not in the first answer) data factory with a unique user | added (`data/user_factory.py`) | Registration needs a unique e-mail on every run. |
| (not in the first answer) `Faker` | used for names and addresses only; the e-mail and the password are made with `uuid` | `pytest-randomly` resets the random seed before each test (section 7). |

What I kept from the first answer is the general discipline (web-first assertions, no
fixed waits, independent tests, session login, traces). What I did not take is everything
that did not serve the five cases of the brief.

## 3. How I reviewed and modified the result

1. I compared the first answer with the brief and cut the parts that the brief does not
   ask for (section 2, table), then I recorded the real site with `playwright codegen --test-id-attribute data-test` and
   with the DevTools console, and compared every locator of the AI with the real one.
2. I walked through the flows by hand (registration, login, reset password, purchase) to
   see the real messages, formats and required fields.
3. I ran every spec file alone with `--headed` and watched it.
4. I ran the whole suite, then the suite in parallel and in random order several times.
5. I read every failure, found its cause and fixed the cause, not the assertion.
6. I checked the rules of the brief with `grep`.
7. I ran the suite against the buggy build, twice, and read the failures one by one.
8. I checked by hand what the buggy build really shows (see `BugReports.md`).

## 4. Problems found and how I fixed them

| # | Problem in the AI result | How I found it | What I changed | Why |
|---|--------------------------|----------------|----------------|-----|
| 1 | The AI wrote the locators from memory. Most of them were right, but not all: the registration form has a required field `house_number` that the first code did not have, and the reset-password confirmation has no `data-test` at all (the AI had invented `forgot-password-success`). | codegen recordings and the DevTools console | Added `house_number` to the factory and to the page object; located the confirmation by its text; checked all other names against the recordings | Locators must match the live application. The brief says not to copy names from a tutorial. |
| 2 | The first codegen command in the instruction had no `--test-id-attribute data-test`, so codegen would look for `data-testid`. | the AI corrected itself in a later answer after I asked for details | Used the command with the flag | `data-test` is the attribute of this application. The first answer (`screenshots/17`) shows the command without the flag. |
| 3 | Passwords like `Pass123word@` or `Serg123@` were refused by the site ("The given password has ..." message). | manual registration in codegen | The factory generates a random password for each run | The site checks passwords; a fixed simple password is not reliable. |
| 4 | Wrong claim in the compare test: the AI assumed that the pliers are cheaper than the hammer. The test failed twice with `assert 'pliers' in 'claw hammer with shock reduction grip'`. | first runs of `test_compare_products.py` | I compared both prices on the site by hand, confirmed that the hammer is cheaper, changed the expectation and added a direct price comparison with a readable message | The assertion did its job: it caught a wrong statement. I did not weaken it. |
| 5 | The first design used the shared seeded account for the login test and for a negative login with a wrong password. The account became locked ("Account locked, too many failed attempts"), and `test_buy_product` failed in its setup. | `ERROR at setup of test_logged_in_customer_buys_a_product`, the page snapshot contained the lock message | The suite now registers its own user once per session (`registered_user`) and signs in with it; the negative login uses an e-mail that does not exist anywhere | A shared public account can be locked by anyone, tests must not depend on it. |
| 6 | The first reset-password negative case used `not-an-email`, but nobody had checked what the site shows for it. | codegen recording: the site shows `email-error` for an empty field | The negative case uses an empty e-mail | Test only behaviour that was observed. |
| 7 | Flaky test: in one of three parallel runs (seed 1751983316) `test_buy_product` failed because `product-title` was not found within 5 s, although the cart badge already showed 1 and the checkout steps were visible. | `python -m pytest -n 4` repeated; the page snapshot in the failure | Default assertion timeout of 15 s (`conftest.py`), an explicit wait for the `/checkout` URL after opening the cart, an explicit wait for the cart table (`CartPage.wait_until_loaded`). After this, 5 parallel runs in a row passed. | A likely cause is that the cart table is loaded by a separate request and is slower with four browsers on a shared site. I did not keep the trace of the failing run, so this cause is a hypothesis supported by the page snapshot. Fixed sleeps are forbidden, so I wait for the state. |
| 8 | Environment problems: pytest was started from Anaconda instead of the virtual environment, and `fixtures.pages_fixture` could not be imported. | `ModuleNotFoundError` in the first runs | Deactivated conda, activated the virtual environment, started `python -m pytest`, made sure all files and `__init__.py` exist | Wrong interpreter and missing files. |
| 9 | The AI assumed that the buggy build behaves like the normal site and opened pages by URL. On the buggy host a direct link such as `/auth/login` returns an Apache 404 (section 6). | the first run against the buggy build, the screenshot and the trace | The page objects of login, registration and forgot-password now open the page like a user: home page, then the "Sign in" link, then the next link. This also works with the hash routes of the buggy build (`/#/auth/login`). | The suite must not depend on the server routing. |
| 10 | Another flaky failure of `test_buy_product`, in a sequential run (seed 234124208, 53.05 s): the "Add to cart" button stayed disabled for 30 s (`element is not enabled`, 56 retries). | `python -m pytest`, 1 failed, 7 passed | I replaced the product by "Bolt Cutters" as a precaution and added a check that gives a readable message when the button is disabled. I did not establish whether the first product was unavailable or the page was stuck. After the failure `tests/test_buy_product.py` alone passed three times in a row (10.59 s, 12.21 s, 14.61 s), so the failure did not repeat. | A disabled button for 30 s is a state of the shared site, not a logic error of the test. The assertions were not weakened. |
| 11 | Another flaky failure in a parallel run (seed 689886712, 44.92 s): at the billing address step the button `proceed-3` (`awnextstep`, the "next step" button of the wizard) stayed disabled for 30 s, which means that the address form was not valid at that moment. | `python -m pytest -n 4`, 1 failed, 7 passed; the log shows `element is not enabled` | The page object now waits until the form is pre-filled from the profile, fills the fields, checks that every value stayed in the field, and if the button is still disabled it fails with the values of all fields in the message. | A likely cause is that the profile data is loaded after the page is shown and can overwrite what the test types. This is a hypothesis: I had no trace of the failing run. The new check turns a silent 30 s timeout into a message that shows the real state of the form. |
| 12 | Another flaky failure, in a sequential run: `test_two_products_can_be_compared_by_price` failed in `read_details()`, `product-name` was not found within 15 s. The page snapshot (site build `v2.5`, built 2026-10-11, Angular 20.0.5) shows the product route with the heading "Related products" but without the product block itself (no name, price or button). Run: `1 failed, 7 passed` in 39.88 s. | the first run of a loop of five sequential runs; the loop stopped at the failure | No code change. I repeated the sequential series with a separate output folder for every run (`--output=artifacts/seq-N`): 12 runs in a row passed (`8 passed`, 23.7 to 25.4 s), so the failure did not repeat. | The product data are most likely loaded by a separate request, and when it is slow or fails the block stays empty. The cause is not established: I did not keep the trace of the failing run, and the failure did not come back. I describe it as rare flaky behaviour of the shared site and I did not hide it with retries. |
| 13 | The first prompt was too general. The AI answered with a framework for "API + UI + CI" (half of the tests at API level, markers, an HTML report, `.env`, a workflow file) and did not mention the five cases, the one-spec-per-case rule or the Page Object rule of the brief. | I compared the answer with the brief (`screenshots/17`, `18`, `19`) | I gave the AI the brief and the five cases in the next prompt and kept only what fits (table in section 2). The API layer, CI, the HTML report and `.env` were not built. | The result must answer the task that is graded. A larger structure is not a better one. Lesson for the next time: put the brief and the acceptance rules into the first prompt. |

## 5. How I verified the result

Environment of all runs: macOS (Apple silicon), Python 3.14.6, pytest 9.1.1,
pytest-playwright 0.10.0, pytest-xdist 3.8.0, pytest-randomly 5.0.0, pytest-rerunfailures
16.7.0, Faker 40.43.0, Chromium 153 (Chrome for Testing). These versions are newer than the
ones in the first AI answer (pytest 8.3, pytest-playwright 0.5, xdist 3.6): I installed the
current versions and did not copy the pinned list.


* Every spec alone with `--headed`: all green (after the fixes of problems 4 and 5).
* Sequential `python -m pytest`: **8 passed** in 29.88 s and in 24.74 s; one sequential run
  failed (problem 10, `1 failed, 7 passed` in 53.05 s).
* Parallel runs `python -m pytest -n 4`:
  * before the fix of problem 7: 3 runs, 2 times `8 passed`, 1 time `1 failed, 7 passed`;
  * after the fix of problem 7: 5 runs in a row, each `8 passed` (13.6 to 15.7 s);
  * later: 3 runs, 2 times `8 passed`, 1 time `1 failed, 7 passed` (problem 11);
  * after the change of the billing step (problems 10 and 11): 15 runs in a row, each
    `8 passed` (11.4 to 17.8 s);
* Sequential series after the change: run 1 of 5 failed (`1 failed, 7 passed` in 39.88 s,
  problem 12) and the series stopped at the failure. The series repeated with a separate
  output folder for every run (`--output=artifacts/seq-N`): 12 runs in a row, each
  `8 passed` (23.7 to 25.4 s).
* Final check before the hand-in: `python -m pytest` gave `8 passed` (27.5 s) and
  `python -m pytest -n 4`, run three times, gave `8 passed` each time (12.8 to 13.6 s).
* So the suite is stable most of the time, but it is not free of flaky behaviour on the
  shared public site. Problems 7, 10 and 11 are of the same kind: a button of the shop stays
  disabled longer than the test waits; problem 12 is a product page that did not show its
  data in time.
* Rules of the brief, checked with `grep`, all three results empty:
  * no `wait_for_timeout` and no `time.sleep` in `tests`, `pages`, `fixtures`;
  * no `get_by` and no `locator(` in `tests/` (locators only in page objects);
  * no `nth(`, XPath or CSS selectors in `tests`, `pages`, `fixtures`.
* Trace viewer: `python -m pytest tests/test_login.py -q --tracing on --output=artifacts/check`
  (2 passed in 7.62 s), then `playwright show-trace` on the trace of the invalid-login
  test (screenshot 10).
* A green run with a screenshot of every test: `python -m pytest --screenshot on
  --output=screenshots/run-results` gave `8 passed` in 28.14 s.

## 6. The buggy build

### 6.1 First run: direct URLs (inconclusive)

```bash
python -m pytest --base-url=https://with-bugs.practicesoftwaretesting.com -v -rA
```

Result: **1 passed, 5 failed, 2 errors** in 190.27 s (`evidence/buggy-run.txt`).

All seven failures were **timeouts while waiting for an element**, not failed assertions.
The screenshot of a failed test shows the Apache page "Not Found"
(`screenshots/09-buggy-404-not-found.png`). The network log of the trace shows that the
first request, `GET https://with-bugs.practicesoftwaretesting.com/auth/login`, returned
**404**. All seven tests started by opening an application route by URL; the only test
that passed started at `/` and then worked inside the application.

Conclusion of this run: on the buggy host a direct link to an application route gives a
server 404 (most likely the server has no fallback to the single-page application; I did
not check the server configuration). The run said nothing about the defects of the buggy
application, so I did not report anything. This was problem 9.

### 6.2 Second run: pages opened through the menu

After the change of problem 9 I ran the suite again (`evidence/buggy-run-2.txt`):

Result: **2 passed, 4 failed, 2 errors** in 136.37 s.

| Test | Result | What the output says |
|---|---|---|
| `test_invalid_credentials_show_error` | passed | the login page opened through the menu and showed the error |
| `test_two_products_can_be_compared_by_price` | passed | no difference found in the prices |
| `test_valid_credentials_open_account_page` | error in setup | registration fixture: timeout waiting for `get_by_test_id("postal_code")` |
| `test_logged_in_customer_buys_a_product` | error in setup | same |
| `test_new_customer_can_register_and_log_in` | failed | same timeout, `postal_code` (page URL `.../#/auth/register`) |
| `test_registration_with_existing_email_is_rejected` | failed | same timeout, `postal_code` |
| `test_known_email_gets_confirmation` | failed | assertion: `get_by_text("page.forgot-password.confirm")` not visible within 15 s |
| `test_empty_email_shows_error` | failed | assertion: `email-error` not visible within 15 s |

This time the application opened, so the results show behaviour of the buggy build.
What I saw in the output:

* **Routes use a hash** (`https://with-bugs.../#/auth/register`). The pages now open and
  the URL checks still pass, because they search for `/auth/login` inside the URL.
* **Registration form.** The fields first name, last name, date of birth and country were
  filled, and the test failed at the postal code: no element with `data-test="postal_code"`
  was found in 30 s. On the normal site the field exists. Because of this the registration
  fixture failed, and four tests could not run their own checks (two register tests, the
  valid login and the purchase). They are blocked, not passed.
* **Forgot password, known e-mail.** After the e-mail was submitted, the page snapshot
  shows the "Forgot Password" form with the e-mail still in the field and no message. On
  the normal site the confirmation text appears.
* **Forgot password, empty e-mail.** The page snapshot shows an empty field and no error
  message. On the normal site the error `email-error` appears.
* **Menu (seen only in the failure snapshots, not asserted by my tests).** The menu item
  that should read "Contact" reads "Contakt", and the "Home" link points to `#/contact`.
  On the normal site they read "Contact" and "Home" and point to `/contact` and `/`.

These are observations of an automated run. Whether each one is a defect of the buggy
build or only a difference of an attribute or of a text was checked by hand; the results,
the steps and the status of every item are in [BugReports.md](BugReports.md). I count as a
defect only an item that I could see by hand. An item that I could not confirm is not a
defect.

What the two failed reset-password tests show: my assertions can fail on the behaviour of
the application, not only on a wrong locator or a timing problem. I did not change any
assertion to make the buggy run green.

What I cannot claim: the registration problem blocks the login and the purchase flows on
the buggy build, so I do not know whether those flows have defects there.

## 7. Decisions and justification

* **Page objects with business actions.** The spec says what is checked, the page object
  knows how the page works. A locator never appears in a spec, so a changed `data-test`
  name is fixed in one place.
* **Own user instead of seeded accounts.** See problem 5. The tests do not depend on the
  state of a shared account and cannot lock it.
* **Assertions in page objects.** The business checks (what the user must see) are only in
  the specs. Page objects and fixtures contain only readiness checks that make a step
  reliable: the URL after navigation, a button that must be enabled, a form that must be
  pre-filled. They fail with a readable message (problems 10 and 11).
* **Login once per session.** Logging in through the UI before every test is slow and
  makes many tests fail when the login page breaks. The login test itself still uses the UI.
  With `pytest-xdist` a session fixture exists once per worker, so a run with `-n 4` registers
  up to four users, one per worker. This is intended: workers do not share an account.
* **`uuid` for e-mail and password.** `pytest-randomly` resets the random seed of Faker
  before each test, so Faker alone could give the same values to different tests. A `uuid`
  is unique across repeated and parallel runs.
* **Opening pages through the menu.** It is what a user does and it works on both builds
  (plain routes and hash routes).
* **Cash on delivery.** I checked this flow by hand. The card form has strict formats and
  adds little to the case "buy a product".
* **Comparison test.** The shop has no compare feature, so the test captures name and
  price of two products and asserts the stated comparison, as the brief allows.
* **Waiting.** No fixed sleeps. Web-first assertions with a 15 s timeout and explicit
  waits for states, because the public site answers with a varying delay.
* **Readable failures.** Where a button of the shop can stay disabled, the page object
  checks it with a message (and prints the form values) instead of waiting 30 s without
  explanation.
* **No automatic retries.** `pytest-rerunfailures` is installed for CI only. A retry would
  hide the flaky behaviour described in problems 7, 10, 11 and 12, so the suite does not use it.
* **Buggy build.** I did not change assertions to get a green run, and I did not call a
  difference a defect before I saw it by hand.
* **Reset password.** The confirmation has no `data-test`; I located it by its text, which
  is the raw translation key `page.forgot-password.confirm`. I regard this as a possible
  localisation defect of the site, but I did not investigate it further.

## 8. Limits and what I would improve

* The suite is not free of flaky behaviour on the shared public site (problems 7, 10, 11,
  12). Problems 10 and 11 did not appear again in 15 parallel runs, but a new one
  (problem 12) appeared in a sequential run. With the trace of every failing run the causes
  could be confirmed instead of guessed.
* The negative registration check asserts only that the user stays on the registration
  page. It should assert the visible duplicate-e-mail message.
* The price comparison depends on the current prices of a shared site.
* The duplicate-e-mail check and the reset-password test depend on the seeded customer
  `customer@practicesoftwaretesting.com` existing on the site.
* `expect.set_options(timeout=15_000)` changes only the assertions. Actions such as `click`
  and `fill` keep the default 30 s, which is why the failures of problems 10 and 11 took
  30 s to appear. A shorter explicit wait before the click would give the message faster.
* Each parallel run registers new users on the shared site (one per worker plus the users of
  the registration tests) and there is no clean-up.
* On the buggy build the registration problem blocks four tests. A separate test user created
  through the API would let the login and purchase tests run there.
* Card payment, favourites, filters, sorting and the profile page are not covered.
* A CI workflow (GitHub Actions) with `--reruns 2` only in CI would run the suite on every
  push. I did not add it.

