"""Страница регистрации ParaBank. Методы возвращают self — «цепочка вызовов»."""
import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.data import User
from utils.metrics import MetricsCollector


class RegistrationPage(BasePage):
    FIELDS = {
        "first_name": "customer.firstName",
        "last_name": "customer.lastName",
        "address": "customer.address.street",
        "city": "customer.address.city",
        "state": "customer.address.state",
        "zip_code": "customer.address.zipCode",
        "phone": "customer.phoneNumber",
        "ssn": "customer.ssn",
        "username": "customer.username",
        "password": "customer.password",
        "confirm": "repeatedPassword",
    }
    FORM = (By.ID, "customerForm")
    SUBMIT = (By.CSS_SELECTOR, "#customerForm input[value='Register']")
    TITLE = (By.CSS_SELECTOR, "#rightPanel h1.title")
    RESULT_TEXT = (By.CSS_SELECTOR, "#rightPanel p")

    def __init__(self, driver, url, metrics: MetricsCollector = None):
        super().__init__(driver, url)
        self.metrics = metrics

    # ---------- локаторы ----------
    def _input(self, field: str):
        return (By.ID, self.FIELDS[field])

    def _error(self, field: str):
        return (By.ID, f"{self.FIELDS[field]}.errors")

    def _record(self, name, ms):
        if self.metrics:
            self.metrics.add(name, ms)

    # ---------- действия ----------
    @allure.step("Открыть форму регистрации и замерить время загрузки")
    def open_page(self):
        self.open()
        self.find_visible(self.FORM)
        # Navigation Timing API: ждём завершения события load и берём длительность
        self.wait.until(lambda d: d.execute_script(
            "const n = performance.getEntriesByType('navigation')[0]; return n && n.loadEventEnd > 0;"))
        load_ms = self.js("return performance.getEntriesByType('navigation')[0].loadEventEnd;")
        self._record("page_load_ms", load_ms)
        return self

    @allure.step("Заполнить поле {field} значением {value}")
    def fill(self, field: str, value: str):
        return self.type_text(self._input(field), value)

    @allure.step("Заполнить форму данными пользователя")
    def fill_form(self, user: User, skip: tuple = ()):
        import time
        start = time.perf_counter()
        for field in self.FIELDS:
            if field in skip:
                continue
            self.fill(field, getattr(user, field))
        self._record("fill_form_ms", (time.perf_counter() - start) * 1000)
        return self

    @allure.step("Отправить форму и дождаться ответа сервера")
    def submit(self):
        import time
        button = self.find(self.SUBMIT)
        start = time.perf_counter()
        button.click()
        self.wait_stale(button)
        self._record("form_response_ms", (time.perf_counter() - start) * 1000)
        return self

    # ---------- проверки ----------
    @allure.step("Проверить, что регистрация прошла для {username}")
    def should_be_registered(self, username: str):
        title = self.get_text(self.TITLE)
        assert title == f"Welcome {username}", f"Неожиданный заголовок: {title!r}"
        text = self.get_text(self.RESULT_TEXT)
        assert "Your account was created successfully" in text, f"Неожиданный текст: {text!r}"
        return self

    @allure.step("Проверить ошибку поля {field}: {expected}")
    def should_see_error(self, field: str, expected: str):
        actual = self.get_text(self._error(field))
        assert expected in actual, f"Для {field} ожидалось {expected!r}, получено {actual!r}"
        return self

    @allure.step("Проверить, что нет сообщения об ошибке у поля {field}")
    def should_not_see_error(self, field: str):
        assert not self.is_visible(self._error(field), timeout=1), f"Неожиданная ошибка у поля {field}"
        return self

    @allure.step("Проверить, что страница не показывает технических ошибок")
    def should_not_leak_errors(self):
        source = self.page_source.lower()
        for marker in ("sqlexception", "stack trace", "java.lang", "internal error", "org.hibernate"):
            assert marker not in source, f"В ответе найден технический маркер: {marker}"
        return self

    @allure.step("Получить тип поля {field}")
    def field_type(self, field: str) -> str:
        return self.get_attribute(self._input(field), "type")

    @allure.step("Получить HTTP-метод формы")
    def form_method(self) -> str:
        return (self.get_attribute(self.FORM, "method") or "get").lower()
