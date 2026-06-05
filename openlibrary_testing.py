"""
OpenLibrary Automated Test Suite
Playwright + pytest (Python)

Run:  pytest openlibrary_testing.py -v
"""

import re
import pytest
from urllib.parse import quote
from playwright.sync_api import Page, expect
from PageClasses import SearchPage, BookDetailPage, AuthorPage, SubjectPage

# ============================================================
# SEARCH FUNCTIONALITY
# ============================================================


# [AI-generated]
# Verifies that searching for a well-known title returns at least one matching result.
# This is the most basic smoke test — if core search is broken, nothing else matters.
def test_known_title_search_returns_results(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("The Great Gatsby")

    expect(search.search_results.first).to_be_visible()
    first_result = search.search_results.first.text_content()
    assert "gatsby" in first_result.lower()


# [AI-generated]
# Verifies that searching by author name surfaces books by that author.
# Author-based search is a primary use case distinct from title search.
def test_author_name_search_returns_books(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("George Orwell")

    expect(search.search_results.first).to_be_visible()
    body_text = page.text_content("body").lower()
    assert re.search(r"orwell|1984|animal farm", body_text)


# [AI-generated]
# Verifies that a very long search string (500 chars) is handled gracefully.
# Long inputs can trigger URL length limits or server-side truncation issues.
def test_very_long_search_string_is_handled(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("a" * 500)

    ready_state = page.evaluate("document.readyState")
    assert ready_state == "complete"
    assert not re.search(r"500|crash", page.title().lower())


# [AI-generated]
# Checks that the search results page renders a "next page" link and that clicking it
# loads a second page of results for a popular query.
def test_search_pagination_loads_page_two(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("science fiction")

    expect(search.search_results.first).to_be_visible()

    next_link = page.locator("a[href*='page=2'], a.next, a[rel='next'], .pagination a")
    expect(next_link.first).to_be_visible()
    next_link.first.click()
    page.wait_for_load_state("networkidle")

    assert re.search(r"page=2|offset=", page.url)


# [My work]
# This test case tests the search input field
# The task is to submit too many characters in the search field
# and find out how the website behaves
def test_empty_search_does_not_crash(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("a" * 500)

    ready_state = page.evaluate("document.readyState")
    assert ready_state == "complete"
    assert not re.search(r"500|crash", page.title().lower())


# [My Work]
# In this test case, I am validating what how will the website behave
# Whenever you don't write anything in the input field
# a.k.a empty query
def test_search_input_retains_value_on_results_page(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("")

    page_ready = page.evaluate("document.readyState")
    assert page_ready == "complete"
    assert "500" not in page.url
    assert "400" not in page.url
    assert "error" not in page.url


# [My Work]
# This test case is testing the dropdown field
# There are many options in the dropdown
# One of the option is "Title" field, where the book must be queried by title
# This test case is validating if the website is really searching the book via title
def test_search_type_selector_title_mode(page: Page):
    search = SearchPage(page)
    search.goto()

    type_select = page.locator('select[name="type"], #search-type-select')
    if type_select.is_visible():
        type_select.select_option(label=re.compile(r"title", re.IGNORECASE))

    search.search("Hobbit")
    expect(search.search_results.first).to_be_visible()
    first_result = search.search_results.first.text_content()
    assert "hobbit" in first_result.lower()


# [My work]
# This test case validates what will happen if the book is searched using special characters
def test_special_characters_do_not_cause_error_page(page: Page):
    search = SearchPage(page)
    search.goto()

    special_characters = ["<script>", "' OR 1=1", "!@#$%^&*()", "日本語"]
    for char in special_characters:
        search.search(char)
        title = page.title().lower()
        assert not re.search(r"500|error|exception", title), (
            f"Error page detected for query: {char!r}"
        )


# ============================================================
# BOOK DETAIL PAGES
# ============================================================


# [AI-generated]
# Checks that navigating to a valid ISBN URL loads a page with the book title visible.
def test_book_detail_loads_for_valid_isbn(page: Page):
    book = BookDetailPage(page)
    book.goto_by_isbn("9780743273565")  # The Great Gatsby

    expect(book.title).to_be_visible()
    assert len(book.title.text_content()) > 0


# [AI-generated]
# Tests the full navigation flow: search result → book detail page.
def test_clicking_search_result_navigates_to_book_page(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("To Kill a Mockingbird")
    expect(search.search_results.first).to_be_visible()

    first_link = page.locator(".searchResultItem a, .bookList a").first
    first_link.click()
    page.wait_for_load_state("networkidle")

    assert re.search(r"openlibrary\.org/(works|books|isbn)", page.url)


# [My Workd]
# This test case validates if error is thrown after submitting an invalid url 
# or the book isn't found 
def test_nonexistent_book_id_shows_not_found(page: Page):
    response = page.goto("https://openlibrary.org/works/OL9999999999W")
    status = response.status
    body_text = page.text_content("body").lower()

    assert status == 404 or "not found" in body_text or "doesn't exist" in body_text or "no books directly matched your search." in body_text


# ============================================================
# AUTHOR PAGES
# ============================================================


# [AI-generated]
# Verifies that a known author page loads with the author's name visible.
def test_author_page_displays_name(page: Page):
    author = AuthorPage(page)
    author.goto_by_id("OL23919A")  # J.K Rowling

    expect(author.author_name).to_be_visible()
    assert "j. k. rowling" in author.author_name.text_content().lower()

# ============================================================
# SUBJECT BROWSING
# ============================================================


# [AI-generated]
# Verifies that a common subject page loads and displays books.
def test_subject_page_loads_books_for_popular_subject(page: Page):
    subject = SubjectPage(page)
    subject.goto_by_subject("fantasy")

    expect(subject.subject_title).to_be_visible()
    assert subject.book_list.count() > 0

# [My Work]
# This test case validates what will happen when you request a high page offset on a large subject 
def test_large_subject_high_offset_still_renders(page: Page):
    page.goto("https://openlibrary.org/subjects/history?offset=200")
    page.wait_for_load_state("networkidle")

    body = page.text_content("body")
    assert not re.search(r"500|server error", body, re.IGNORECASE)
    assert len(page.title()) > 0


# ============================================================
# ERROR HANDLING
# ============================================================


# [AI-generated]
# Confirms that the REST API returns a 404 (not 500) for an unknown work ID.
def test_api_returns_404_for_unknown_work_id(page: Page):
    response = page.goto("https://openlibrary.org/works/OL000000000W.json")
    assert response.status == 404


# [My Work]
# This test case validates that whenever you go to a non existing page, the error is thrown
def test_invalid_url_path_returns_404(page: Page):
    response = page.goto("https://openlibrary.org/test/sandro123")

    status = response.status
    body = page.text_content("body").lower()
    assert status == 400 or "not found" in body or "page not found" in body


# [My work]
# This test case searches the non existing book using the search field 
# and validates if "no result found" or something similar is returned
def test_zero_result_search_shows_no_results_message(page: Page):
    search = SearchPage(page)
    search.goto()
    search.search("dowaijdhoawjdoajwdoiajwdoaiwdaiowjdoawdoajwdoiajdoj")

    body = page.text_content("body").lower()
    assert re.search(r"no results|no matches|0 matches|didn't find", body), (
            "Expected a no-results or offline message but found neither"
            )


# ============================================================
# EDGE CASES (discoverable only by using the site)
# ============================================================


# [AI-generated]
# Verifies the JSON API for a known work returns the expected fields.
def test_json_api_for_known_work_returns_expected_fields(page: Page):
    response = page.goto(
        "https://openlibrary.org/works/OL45804W.json"
    )  # Fantastic Mister Fox
    assert response.status == 200

    data = response.json()
    assert "title" in data
    assert "key" in data
    assert "type" in data


# [My Work]
# After clicking on the Author, and going to the author page, I clicked sorting field and chose "First Published" books
# Some of the book covers  are not being shown, either it's being correctly rendered (the image itself is broken)
# Or the image is pointing to the wrong file
# So this automated code will test that field
def test_author_page_sorted_by_first_published_covers_are_rendered(page: Page):
    page.goto("https://openlibrary.org/authors/OL23919A?sort=first_published")
    page.wait_for_load_state("networkidle")

    covers = page.locator('img[itemprop="image"]')
    assert covers.count() > 0, "No cover images found on the page"

    broken_images = []

    for i in range(covers.count()):
        cover = covers.nth(i)
        src = cover.get_attribute("src")
        box = cover.bounding_box()

        if not src or src == "":
            broken_images.append(f"Image {i}: src is empty or missing")
        elif box is None:
            broken_images.append(f"Image {i}: not in visible DOM — src was {src}")
        elif box["width"] == 0 or box["height"] == 0:
            broken_images.append(f"Image {i}: has zero dimensions — src was {src}")

    assert len(broken_images) == 0, (
        f"{len(broken_images)} cover(s) not rendered correctly:\n" +
        "\n".join(broken_images)
    )



# [My Work]
# Found out that whenever you search a book for example "OL1701743M" 
# this book claims that it has 1179 editions but only 13 are displayed on the page 
# This test checks that the number shown in the editions count label
# matches the actual number of edition entries rendered on the page.
def test_editions_displayed_match_stated_count(page: Page):
    page.goto("https://openlibrary.org/works/OL1701743M/editions")
    page.wait_for_load_state("networkidle")

    body_text = page.text_content("body")
    stated_count = re.search(r"(\d+)\s+editions", body_text, re.IGNORECASE)
    assert stated_count, "Could not find editions count on page"

    edition_entries = page.locator(".edition, .bookList li, .searchResultItem, li[itemtype*='Book']")
    actual_count = edition_entries.count()

    assert actual_count > 0, "No edition entries found on page"
    assert actual_count >= int(stated_count.group(1)), (
        f"Page claims {stated_count.group(1)} editions but only {actual_count} are displayed"
    )

# [My work]
# Found out tha when you search a book in Lists page another book is being returned
# For example in browse when you select Lists and type "Uncle Tom's Cabin"
# "Civil War" is returned
def test_list_search_returns_relevant_results(page: Page):
    page.goto("https://openlibrary.org/lists")
    page.wait_for_load_state("networkidle")

    search_input = page.locator('input[name="q"], input[type="search"]').first
    if search_input.is_visible():
        search_input.fill("Uncle Tom's Cabin")
        search_input.press("Enter")
        page.wait_for_load_state("networkidle")

    body_text = page.text_content("body").lower()
    assert "uncle tom" in body_text, (
        "Search for 'Uncle Tom's Cabin' did not return relevant results"
    )
    assert "civil war" not in body_text, (
        "Search for 'Uncle Tom's Cabin' incorrectly returned 'Civil War'"
    )

# [My work]
# Found out that whenever you search a book by work id, another title is returned
# "OL45804W" This is the work id for Fantastic Mr. Fox, but whenever you search with it
# Spanish version is returned called "El Superzorro"
# Also these two books have the same work ID, whereas the IDs must be unique 
def test_work_id_resolves_to_correct_language(page: Page):
    page.goto("https://openlibrary.org/works/OL45804W")
    page.wait_for_load_state("networkidle")

    title = page.locator('h1[itemprop="name"], h1.work-title').first
    expect(title).to_be_visible()

    title_text = title.text_content().lower()
    assert "fantastic mr. fox" in title_text, (
        f"Expected English title but got: {title_text}"
    )
    assert "superzorro" not in title_text, (
        "Work ID resolved to Spanish edition instead of English"
    )

