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
git clone https://github.com/SergeyK123/toolshop-playwright-python
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
| CI mode on this machine (one shard of four) | `CI=true python -m pytest -p no:randomly --splits 4 --group 1 --reruns 2 -n 2` |

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
├── .github/
│   └── workflows/
│       └── playwright.yml  CI: 4 shards, report merge, artefacts
├── conftest.py            test id attribute (data-test), assertion timeout, "only" guard for CI
├── pytest.ini             base URL, run options, marker "only"
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
├── screenshots/           screenshots used in Review.md (ci-*.png belong to the CI work)
└── evidence/              logs of the runs against the buggy build
    ├── buggy-run.txt
    └── buggy-run-2.txt
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

## CI

[![Playwright Tests](https://github.com/SergeyK123/toolshop-playwright-python/actions/workflows/playwright.yml/badge.svg?branch=main)](https://github.com/SergeyK123/toolshop-playwright-python/actions/workflows/playwright.yml)

**CI system:** GitHub Actions. The repository already lives on GitHub, no separate server
is needed, and a matrix makes sharding simple. The workflow is
`.github/workflows/playwright.yml`.

**Runner (important).** The test jobs run on a *self-hosted* runner (macOS, ARM64, my own
laptop), not on `ubuntu-latest`. On GitHub-hosted runners the target site answers every
request with a Cloudflare page "Performing security verification / Verify you are human"
(HTTP 403, header `cf-mitigated: challenge`). The Angular application never starts, so every
test waits 30 s for the first element and fails. The screenshot and the trace of such a run
are in `screenshots/ci-00-cloudflare.png` and described in Review.md, problem 19. Test code
was not changed for this. The `merge-reports` job does not open the site and runs on
`ubuntu-latest`. A run needs the runner to be online; otherwise its jobs wait in the queue.

**Pipeline**

* Triggers: every `push`, every `pull_request`, and a manual `workflow_dispatch`.
* `actions/checkout`, a guard step that fails the run if `mark.only` is found in `tests/`.
* Dependencies: a virtual environment (`python3 -m venv .venv`),
  `pip install -r requirements.txt`, the pip cache restored with `actions/cache`
  (the log of the second run shows `Cache restored`, `screenshots/ci-02-cache-restored.png`).
* Browser: `playwright install --with-deps chromium`.
* Tests: the **full** suite, no `-k` and no `-m`, split into **4 shards** with `pytest-split`
  (`--splits 4 --group i`). Shards run as parallel matrix jobs, `fail-fast: false`.
* Job `merge-reports`: downloads the JUnit file of every shard and merges them with
  `junitparser` into one XML, then renders one HTML report with `junit2html`.
* Artefacts, kept 14 days: `test-results-1...4` (traces, screenshots of failed tests, JUnit),
  `playwright-report` (merged HTML), `junit-report` (merged XML). The per-shard
  `junit-1...4` files are kept 1 day, they are only an intermediate step.
* Run graph: `screenshots/ci-01-run-graph.png`, artefacts: `screenshots/ci-03-artifacts.png`.

**CI settings** (`CI=true` and `PYTEST_ADDOPTS` in the workflow)

| Setting | Value | Why |
|---|---|---|
| Reruns | `--reruns 2` (`pytest-rerunfailures`) | a rare flaky failure of the shared site is marked as a rerun instead of a red run |
| Workers inside a shard | `-n 2` (`pytest-xdist`) | two browsers per shard |
| JUnit | `--junitxml=reports/junit-N.xml` | input of the report merge |
| Trace | `--tracing retain-on-failure` (from `pytest.ini`) | trace of every failed attempt |
| Random order | switched off with `-p no:randomly` in CI | see the note below |
| Focused tests | `@pytest.mark.only` fails the run (`conftest.py` and a workflow step) | analogue of `forbidOnly` |

**Differences from the TypeScript version of the guide.** The guide targets the Node
test runner. This project is Python, so:

| Guide | This project |
|---|---|
| `forbidOnly` | custom marker `only`, forbidden in CI by a hook in `conftest.py` |
| `retries: 2` | `--reruns 2` |
| `--shard=i/4` | `pytest-split`, `--splits 4 --group i` |
| `blob` reporter and `merge-reports` | JUnit files merged with `junitparser`, HTML by `junit2html` |
| `trace: 'on-first-retry'` | does not exist in pytest-playwright; `retain-on-failure` is used |
| `npm ci` and the npm cache | `pip install -r requirements.txt` and `actions/cache` on the pip cache |

`pytest-randomly` is switched off in CI because every shard must receive the same ordered
list of tests; with a different order per shard `pytest-split` could run a test twice or
not at all. In the CI check the four shards ran 2 + 2 + 2 + 2 tests, 8 `testcase` entries
in total. Locally the random order stays on.

### Runtime

Numbers come from the log of the self-hosted runner (job start to job end, `Total` is from
the start of the first job to the end of the last one). The page of a run in GitHub shows a
few seconds more because of the `merge-reports` job.

| Configuration | Total run time | Longest single job | Runs |
| --- | --- | --- | --- |
| 1 job, no sharding (`--splits 1`) | about 1 min 17 s (median of 3: 88 s, 75 s, 77 s) | 1 min 17 s | [[FILL link to run 1]], [[FILL link to run 2]], [[FILL link to run 3]] |
| 4 shards + merge | about 5 min 3 s (median of 5: 4:50, 4:57, 5:03, 5:10, 5:29) | 1 min 20 s (median of 5: 88, 77, 75, 86, 80 s) | [[FILL link to a 4-shard run]] |

Conclusion: on one self-hosted machine the four shards run one after another and every shard
repeats the setup (dependencies, browser, checkout, about a minute of a 70 to 80 second
job), so sharding made the run about four times **slower**; it would pay off only with
several runners at the same time or with a much longer suite.

### Running the CI configuration locally

```bash
export CI=true
for g in 1 2 3 4; do
  python -m pytest -p no:randomly --splits 4 --group $g --reruns 2 -n 2 \
    --junitxml=reports/junit-$g.xml
done
unset CI
grep -ho '<testcase' reports/junit-*.xml | wc -l      # expected: 8
```

### Self-hosted runner: safety and upkeep

* The runner executes code of the workflows on the laptop. The repository settings
  *Actions, General, Fork pull request workflows* require approval for outside
  collaborators, and pull requests from strangers must not be approved.
* The runner folder has no spaces in its path (`~/actions-runner`): a space broke every
  `run:` step (Review.md, problem 22).
* The laptop must be on, awake and without a VPN while the jobs run
  (`caffeinate -i ./run.sh`). Past runs stay available through the links above.
* [[FILL after the hand-in, one of the two sentences: "The runner is still registered." or
  "The runner was removed after the hand-in; links to past runs stay valid."]]

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
* The site sits behind Cloudflare. Requests from GitHub-hosted runners get a
  "Verify you are human" page, so the CI jobs run on a self-hosted runner (see CI).
* Sharding on one runner does not make the run faster (see the runtime table).