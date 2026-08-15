from threading import Thread
from time import sleep

from page import ChartPage, TablePage
from page_collection import PageCollection, Page


class DataUpdateThread(Thread):
    def __init__(self, page_collection: PageCollection) -> None:
        super().__init__(target=self.__run, daemon=True)
        self.page_collection = page_collection
        self.update_dict: dict[Page, int] = {}
        for page in page_collection.pages:
            self.update_dict[page] = DataUpdateThread.get_update_delay(page)

    @staticmethod
    def get_update_delay(page: Page) -> int:
        if isinstance(page, ChartPage):
            return page.update_delay
        elif isinstance(page, TablePage):
            return page.update_delay
        raise Exception()

    @staticmethod
    def update_page(page: Page) -> None:
        if isinstance(page, ChartPage):
            page.data.append(page.data_acquirere())
        elif isinstance(page, TablePage):
            page.data = page.data_acquirere()
        else:
            raise Exception()

    def __run(self) -> None:
        for page in self.update_dict.keys():
            DataUpdateThread.update_page(page)
            page.dirty = True
        while True:
            sleep(5)
            for key, value in self.update_dict.items():
                print(f"{key} -> {value}")
                if value <= 5:
                    print("Updating page")
                    DataUpdateThread.update_page(key)
                    self.update_dict[key] = key.update_delay
                    key.dirty = True
                else:
                    print("Skipping updating page")
                    self.update_dict[key] = value - 5
