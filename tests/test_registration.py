import allure
import pytest

from pages.registration_page import RegistrationPage
from utils.data import make_user


@pytest.fixture
def page(driver, url, metrics):
    return RegistrationPage(driver, url, metrics)


@allure.epic("ParaBank")
@allure.feature("Регистрация")
class TestRegistration:

    @allure.story("Позитивный сценарий")
    @allure.title("Успешная регистрация с корректными данными")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.metrics
    def test_successful_registration(self, page, metrics):
        user = make_user()
        with metrics.measure("registration_total_ms"):
            (page.open_page()
                 .fill_form(user)
                 .submit()
                 .should_be_registered(user.username))

    @allure.story("Негативные сценарии")
    @allure.title("Пустая форма: все обязательные поля подсвечены ошибками")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_empty_form(self, page):
        (page.open_page()
             .submit()
             .should_see_error("first_name", "First name is required")
             .should_see_error("last_name", "Last name is required")
             .should_see_error("address", "Address is required")
             .should_see_error("city", "City is required")
             .should_see_error("state", "State is required")
             .should_see_error("zip_code", "Zip Code is required")
             .should_see_error("ssn", "Social Security Number is required")
             .should_see_error("username", "Username is required")
             .should_see_error("password", "Password is required")
             .should_see_error("confirm", "Password confirmation is required"))

    @allure.story("Негативные сценарии")
    @allure.title("Пароль и подтверждение не совпадают")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_passwords_do_not_match(self, page):
        user = make_user(confirm="Different#999")
        (page.open_page()
             .fill_form(user)
             .submit()
             .should_see_error("confirm", "Passwords did not match"))

    @allure.story("Негативные сценарии")
    @allure.title("Без имени регистрация невозможна")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_missing_first_name(self, page):
        user = make_user()
        (page.open_page()
             .fill_form(user, skip=("first_name",))
             .submit()
             .should_see_error("first_name", "First name is required"))

    @allure.story("Негативные сценарии")
    @allure.title("Без SSN регистрация невозможна")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_missing_ssn(self, page):
        user = make_user()
        (page.open_page()
             .fill_form(user, skip=("ssn",))
             .submit()
             .should_see_error("ssn", "Social Security Number is required"))

    @allure.story("Негативные сценарии")
    @allure.title("Без логина регистрация невозможна")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_missing_username(self, page):
        user = make_user()
        (page.open_page()
             .fill_form(user, skip=("username",))
             .submit()
             .should_see_error("username", "Username is required"))

    @allure.story("Негативные сценарии")
    @allure.title("Повторная регистрация с уже занятым логином")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_duplicate_username(self, page, driver):
        user = make_user()
        page.open_page().fill_form(user).submit().should_be_registered(user.username)
        driver.delete_all_cookies()  # выходим из созданной сессии
        (page.open_page()
             .fill_form(user)
             .submit()
             .should_see_error("username", "This username already exists"))
