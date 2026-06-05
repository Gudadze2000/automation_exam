# OpenLibrary Test via Python

This is Automated test suite for [openlibrary.org](https://openlibrary.org),  
built with **pytest** + **playwright-python**.

## Setup

**NOTE** If you don't have [UV astral](https://docs.astral.sh/uv/) installed please run this code:

*For MacOS*
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
*For Windows*
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
## You are all set up. Now let's create an empty directory

```bash
mkdir automated_testing_exam
cd automated_testing_exam
uv init
```
## Now add all of the dependencies 
```bash
uv export --format requirements.txt
```
## After installing dependencies, install chromium engine 
```bash
playwright install chromium
```

## Run all tests

```bash
pytest openlibrary_testing.py -v
```
## File structure

```
openlibrary_testing.py   # Full test suite — annotated [AI-generated] / [My Work]
PageClasses.py           # Page Object Model classes used by the test suite
pytest.ini               # pytest configuration
```

## Notes

- All tests are **read-only** — no accounts created, no data written.
- Tests run sequentially (`-p no:randomly`) to avoid rate-limiting the live site.
- Optional UI elements (e.g. search-type dropdown) are checked with `.is_visible()`  
  before interaction, so tests degrade gracefully if the site changes layout.

## Test Case Explanation
---
There are two types of test cases in this code, **`[AI-Generated]`** and **`[My Work]`**. The AI-generated ones cover standard tests that clode generated. The `[My Work]` ones were written based on my exploration of the site, real bugs and edge cases discovered by actually exploring the website itself.
I also asked *Claude* to leave some of the test case building to me because I really wanted to explore this unknown library by myself.

Here's the brief explanation of every test case in this code:

---

### Search Functionality

| Test | Type | Description |
|------|------|-------------|
| `test_known_title_search_returns_results` | AI-Generated | Searches for "The Great Gatsby" and verifies at least one result appears containing the word "gatsby". Basic smoke test — if this fails, search is broken entirely. |
| `test_author_name_search_returns_books` | AI-Generated | Searches for "George Orwell" and checks that the results page contains his name or one of his well-known works. Validates that author-name queries work distinctly from title queries. |
| `test_very_long_search_string_is_handled` | AI-Generated | Submits a 500-character string and confirms the page loads without crashing or showing a server error. Tests resilience against URL length limits and server-side truncation. |
| `test_search_pagination_loads_page_two` | AI-Generated | Searches for "science fiction", finds the "next page" link, clicks it, and checks the URL reflects page 2. Confirms pagination is functional for high-volume queries. |
| `test_empty_search_does_not_crash` | My Work | Submits a 500-character query and checks the page completes loading without a 500 error in the title. Discovered that extreme input lengths can expose unhandled server errors. |
| `test_search_input_retains_value_on_results_page` | My Work | Submits an empty query and verifies the site does not return a 400/500 HTTP error or navigate to an error URL. Found that blank searches can trigger unexpected error responses. |
| `test_search_type_selector_title_mode` | My Work | Selects "Title" from the search type dropdown (if visible), searches for "Hobbit", and confirms the first result contains that word. Validates that the dropdown mode actually filters results correctly. |
| `test_special_characters_do_not_cause_error_page` | My Work | Submits a series of potentially dangerous inputs (`<script>`, SQL injection, symbols, Japanese characters) one by one and checks that none triggers a server error page. Tests both security resilience and input sanitization. |

---

### Book Detail Pages

| Test | Type | Description |
|------|------|-------------|
| `test_book_detail_loads_for_valid_isbn` | AI-Generated | Navigates directly to The Great Gatsby via its ISBN and confirms the title element is visible and non-empty. |
| `test_clicking_search_result_navigates_to_book_page` | AI-Generated | Searches for "To Kill a Mockingbird", clicks the first result link, and checks the resulting URL is a valid OpenLibrary book or works page. |
| `test_nonexistent_book_id_shows_not_found` | My Work | Navigates to a made-up work ID (`OL9999999999W`) and checks that either a 404 status is returned or the page body contains a "not found" type message. Verifies that invalid IDs are handled gracefully rather than silently. |

---

### Author Pages

| Test | Type | Description |
|------|------|-------------|
| `test_author_page_displays_name` | AI-Generated | Loads J.K. Rowling's author page by her OpenLibrary ID and verifies her name appears in the `h1` heading. |

---

### Subject Browsing

| Test | Type | Description |
|------|------|-------------|
| `test_subject_page_loads_books_for_popular_subject` | AI-Generated | Navigates to the "fantasy" subject page and checks that the title is visible and at least one book entry is rendered. |
| `test_large_subject_high_offset_still_renders` | My Work | Loads the "history" subject page with `offset=200` and confirms the page loads without a server error. Discovered that high offsets on large subjects can sometimes cause unexpected failures. |

---

### Error Handling

| Test | Type | Description |
|------|------|-------------|
| `test_api_returns_404_for_unknown_work_id` | AI-Generated | Hits the JSON API endpoint for a nonexistent work ID and confirms the HTTP status is 404, not 500. |
| `test_invalid_url_path_returns_404` | My Work | Navigates to a completely made-up URL path and verifies the response is a 400 or that the body contains a "not found" message. |
| `test_zero_result_search_shows_no_results_message` | My Work | Searches for a long nonsense string and checks that the results page explicitly communicates that no results were found, rather than rendering an empty or broken page silently. |

---

### Edge Cases (discovered by manual site exploration)

| Test | Type | Description |
|------|------|-------------|
| `test_json_api_for_known_work_returns_expected_fields` | AI-Generated | Fetches the JSON representation of *Fantastic Mr. Fox* and confirms the response includes `title`, `key`, and `type` fields. |
| `test_author_page_sorted_by_first_published_covers_are_rendered` | My Work | Navigates to J.K. Rowling's author page sorted by "First Published" and checks every cover image for a valid `src`, visible DOM presence, and non-zero dimensions. Found that several book covers fail to render correctly under this sort order. |
| `test_editions_displayed_match_stated_count` | My Work | Visits the editions page for a specific work that claims 1179 editions and verifies the number of edition entries actually rendered on the page is consistent with the stated count. Found a discrepancy where only ~13 editions were displayed despite the label claiming over a thousand. |
| `test_list_search_returns_relevant_results` | My Work | Goes to the Lists browse page, searches for "Uncle Tom's Cabin", and checks that the results are relevant — specifically that "Uncle Tom" appears and "Civil War" does not dominate the results. Discovered that list search was returning thematically related but incorrect results. |
| `test_work_id_resolves_to_correct_language` | My Work | Navigates to the work ID for *Fantastic Mr. Fox* (`OL45804W`) and checks that the English title is displayed, not the Spanish edition title "El Superzorro". Found that this work ID was resolving to the Spanish version, suggesting two editions were incorrectly sharing the same unique ID. |


### Last Note:
Please keep in mind that **it was my first time using Playwright**,
therefore building these test cases, and debugging them was very hard. So there may be some errors that you'll see. 


There are some additional bugs, that I found manually, but I am not sure how was I supposed to test it automatically. 
There were a lot of steps to be reproduced when I asked claude. So even AI was unable to build those test cases fully.

Here are the bugs: 
 - Can’t check out already checked out book. Why? they’re electronic copies?
 - After clicking borrow the book, it transfers you to the Internet Archive page, but when you open the website again, it doesn’t update the state of the book. Like it doesn't show that the book is borrowed, in front
 - **OL1701743M** this book shows 1179 editions, but onnly 13  are displayed in the list
 - The same book says *216* pages but *243* are in the actual book
 - After returning the book The UI changes in the my profile > My loans sector. Logically it's not supposed to change
 - The book says on the front-end that it is checked out, but when I click the button itself it transfers me to the book page and “check out” button dissapears and now i am able to borrow the book. It isn't supposed to work like this
 - The book adding option doens’t have deleting option. Whenever the user tries to add a new book, the same user isn't able to delete the said book.
 - In Lists dropdown, whenever I look for "Uncle Tom's Cabin" it returns "Civil War"
 - **The Audio Book:** The system reads the whole book in a robotic way (kind of unexpected) and whenever you want to skip some part, the audio book returnes to the old state. Like it doesn’t let you skip
 - After having the book openend in a new tab, after some time the website automatically returned the book even though i didn’t click “return” now.
 - **OL45804W** — Work id of fantastic mr fox. The english and spanish version have non-unique work ids. So whenever you search this book with this work id, you are trasnferred to spanish version.

# P.S 
## I wrote the markdown file myself, but then I used Claude to rewrite it. Just to give it a better visual.
