from typing import Union
from page import ChartPage, TablePage

Page = Union[ChartPage, TablePage]


class PageCollection:
    def __init__(self) -> None:
        self.pages: list[Page] = []

    def add(self, page: Page) -> None:
        self.pages.append(page)

    def update(self) -> None:
        for page in self.pages:
            if isinstance(page, ChartPage):
                page.data.append(page.data_acquirere())
            elif isinstance(page, TablePage):
                page.data = page.data_acquirere()
