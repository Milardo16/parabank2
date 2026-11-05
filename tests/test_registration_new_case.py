"""Новый тест-кейс практики. Цепочка «требование → правка → проверка» — в docs/CHANGE_CHAIN.md."""
import allure
import pytest

from pages.registration_page import RegistrationPage
from utils.data import make_user


@allure.epic("ParaBank")
@allure.feature("Регистрация")
@allure.story("Расширение сценария")
class TestRegistrationExtended:

    @allure.title("REQ-REG-01: номер телефона необязателен — регистрация проходит без него")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.metrics
    def test_registration_without_phone(self, driver, url, metrics):
        user = make_user(phone="")
        page = RegistrationPage(driver, url, metrics)
        with metrics.measure("registration_without_phone_total_ms"):
            (page.open_page()
                 .fill_form(user)
                 .should_not_see_error("phone")
                 .submit()
                 .should_be_registered(user.username))
