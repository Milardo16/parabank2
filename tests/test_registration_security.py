"""Проверки безопасности формы регистрации (базовый уровень, без инструментов взлома)."""
import urllib.request

import allure
import pytest
from selenium.common.exceptions import NoAlertPresentException

from pages.registration_page import RegistrationPage
from utils.data import make_user

XSS_PAYLOADS = [
    "<script>window.__xss=1</script>",
    "<img src=x onerror=window.__xss=1>",
    "\"><svg onload=window.__xss=1>",
]
SQLI_PAYLOADS = ["' OR '1'='1", "admin'--", "'; DROP TABLE users;--"]


@pytest.fixture
def page(driver, url, metrics):
    return RegistrationPage(driver, url, metrics)


@allure.epic("ParaBank")
@allure.feature("Безопасность регистрации")
@pytest.mark.security
class TestRegistrationSecurity:

    @allure.title("Транспорт: страница регистрации открывается по HTTPS")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_page_served_over_https(self, page, driver):
        page.open_page()
        assert driver.current_url.startswith("https://"), driver.current_url

    @allure.title("Поля пароля скрывают ввод (type=password)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_password_fields_are_masked(self, page):
        page.open_page()
        assert page.field_type("password") == "password"
        assert page.field_type("confirm") == "password"

    @allure.title("Форма отправляется методом POST, а не GET")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_form_uses_post(self, page):
        assert page.open_page().form_method() == "post"

    @allure.title("Пароль не попадает в URL после отправки формы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_password_not_in_url(self, page, driver):
        user = make_user()
        page.open_page().fill_form(user).submit()
        assert user.password not in driver.current_url
        assert "password" not in driver.current_url.lower()

    @allure.title("XSS: скрипт из полей формы не выполняется")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_payload_not_executed(self, page, driver, payload):
        user = make_user(first_name=payload, last_name=payload, address=payload, city=payload)
        page.open_page().fill_form(user).submit()
        with allure.step("Проверить, что JS из payload не выполнился"):
            assert driver.execute_script("return window.__xss") is None, "XSS выполнился"
            with pytest.raises(NoAlertPresentException):
                driver.switch_to.alert

    @allure.title("SQL-инъекция в логине не вызывает технических ошибок")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("payload", SQLI_PAYLOADS)
    def test_sql_injection_in_username(self, page, payload):
        user = make_user(username=payload)
        page.open_page().fill_form(user).submit().should_not_leak_errors()

    @allure.title("Очень длинные значения обрабатываются без падения сервера")
    @allure.severity(allure.severity_level.NORMAL)
    def test_very_long_input(self, page):
        user = make_user(first_name="A" * 5000, address="B" * 5000)
        page.open_page().fill_form(user).submit().should_not_leak_errors()

    @allure.title("Cookie сессии имеют флаги HttpOnly и Secure")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.xfail(reason="Учебное приложение может не выставлять флаги — фиксируем как замечание", strict=False)
    def test_session_cookie_flags(self, page, driver):
        user = make_user()
        page.open_page().fill_form(user).submit()
        cookies = [c for c in driver.get_cookies() if "SESSION" in c["name"].upper()]
        assert cookies, "Cookie сессии не найдена"
        for c in cookies:
            assert c.get("httpOnly"), f"{c['name']}: нет HttpOnly"
            assert c.get("secure"), f"{c['name']}: нет Secure"

    @allure.title("Заголовки безопасности присутствуют в ответе")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.xfail(reason="Учебное приложение может не отдавать заголовки — фиксируем как замечание", strict=False)
    def test_security_headers(self, url):
        with urllib.request.urlopen(url, timeout=15) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
        for h in ("x-content-type-options", "x-frame-options", "content-security-policy"):
            assert h in headers, f"Нет заголовка {h}"
