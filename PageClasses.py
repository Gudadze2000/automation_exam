from playwright.sync_api import Page
from urllib.parse import quote

# ============================================================
# PAGE OBJECT MODEL
# ============================================================

class SearchPage:
    URL = "https://openlibrary.org"

    def __init__(self, page: Page):
        self.page = page

    def goto(self):
        self.page.goto(self.URL)

    def search(self, query: str):
        self.page.wait_for_selector('input[name="q"]', timeout=5000)
        self.page.fill('input[name="q"]', query)
        self.page.press('input[name="q"]', "Enter")
        self.page.wait_for_load_state("networkidle")

    @property
    def search_input(self):
        return self.page.locator('input[name="q"]')

    @property
    def search_results(self):
        return self.page.locator(".searchResultItem")

    @property
    def pagination_next(self):
        return self.page.locator("a.ChoosePage--next, a[rel='next']")

    @property
    def no_results_message(self):
        return self.page.locator(".searchResults--noresults, .no-results")


class BookDetailPage:
    BASE = "https://openlibrary.org"

    def __init__(self, page: Page):
        self.page = page

    def goto_by_isbn(self, isbn: str):
        self.page.goto(f"{self.BASE}/isbn/{isbn}")
        self.page.wait_for_load_state("networkidle")

    def goto_by_work_id(self, work_id: str):
        self.page.goto(f"{self.BASE}/works/{work_id}")
        self.page.wait_for_load_state("networkidle")

    @property
    def title(self):
        return self.page.locator('h1[itemprop="name"], h1.work-title').first

    @property
    def author_link(self):
        return self.page.locator('a[itemprop="author"], .WorkDetail--author a')

    @property
    def subjects_section(self):
        return self.page.locator('.subjects, [data-testid="subjects"], .subject-tag')

    @property
    def description_section(self):
        return self.page.locator(".book-description, .read-more__content")

    @property
    def cover_image(self):
        return self.page.locator('img[itemprop="image"], .cover img, .bookCover')


class AuthorPage:
    BASE = "https://openlibrary.org"

    def __init__(self, page: Page):
        self.page = page

    def goto_by_id(self, author_id: str):
        self.page.goto(f"{self.BASE}/authors/{author_id}")
        self.page.wait_for_load_state("networkidle")

    @property
    def author_name(self):
        return self.page.locator("h1.author-name, h1[itemprop='name']")

    @property
    def works_section(self):
        return self.page.locator(".works, .author-works, .listResults")

    @property
    def work_entries(self):
        return self.page.locator(".bookList li, .listResults li")


class SubjectPage:
    BASE = "https://openlibrary.org"

    def __init__(self, page: Page):
        self.page = page

    def goto_by_subject(self, subject: str):
        self.page.goto(f"{self.BASE}/subjects/{quote(subject)}")
        self.page.wait_for_load_state("networkidle")

    @property
    def subject_title(self):
        return self.page.locator("h1.subject-title, h1")

    @property
    def book_list(self):
        return self.page.locator(".book, .bookList li, .searchResultItem")

    @property
    def pagination_next(self):
        return self.page.locator("a[rel='next'], .pagination-next, a.next")
