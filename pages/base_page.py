"""BasePage — низкоуровневое взаимодействие с браузером (только явные ожидания)."""
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings


class BasePage:
    def __init__(self, driver: WebDriver, url: str, timeout: int = None):
        self.driver = driver
        self.url = url
        self.wait = WebDriverWait(driver, timeout or settings.explicit_timeout)

    @allure.step("Открыть страницу")
    def open(self):
        self.driver.get(self.url)
        return self

    @allure.step("Найти элемент {locator}")
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    @allure.step("Найти видимый элемент {locator}")
    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    @allure.step("Клик по {locator}")
    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        return self

    @allure.step("Ввести текст в {locator}")
    def type_text(self, locator, text: str):
        element = self.find_visible(locator)
        element.clear()
        if text:
            element.send_keys(text)
        return self

    @allure.step("Получить текст {locator}")
    def get_text(self, locator) -> str:
        return self.find_visible(locator).text.strip()

    @allure.step("Получить атрибут {name} у {locator}")
    def get_attribute(self, locator, name: str):
        return self.find(locator).get_attribute(name)

    @allure.step("Проверить наличие элемента {locator}")
    def is_visible(self, locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    @allure.step("Дождаться исчезновения старого элемента (ответ сервера)")
    def wait_stale(self, element):
        self.wait.until(EC.staleness_of(element))
        return self

    @allure.step("Выполнить JS")
    def js(self, script: str, *args):
        return self.driver.execute_script(script, *args)

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    @staticmethod
    def by_id(value: str):
        return (By.ID, value)
