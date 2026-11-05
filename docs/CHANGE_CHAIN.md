# Цепочка: требование → правка → проверка

## Требование
**REQ-REG-01.** Поле «Phone #» на форме регистрации необязательное: пользователь, не указавший телефон,
должен успешно зарегистрироваться, а у поля не должно появляться сообщение об ошибке.

## Правка
| Файл | Изменение |
|---|---|
| `utils/data.py` | `make_user(phone="")` — пустой телефон допустим в данных пользователя |
| `pages/base_page.py` | `type_text` очищает поле и не вводит пустую строку |
| `pages/registration_page.py` | добавлен метод `should_not_see_error(field)` в цепочку проверок |
| `tests/test_registration_new_case.py` | новый тест `test_registration_without_phone`, маркер `regression`, замер `registration_without_phone_total_ms` |

## Проверка
1. `pytest tests/test_registration_new_case.py`
2. Ожидаемый результат: нет ошибки у поля телефона → отображается «Welcome <username>» и «Your account was created successfully».
3. Если тест упал — в Allure приложены скриншот, логи браузера и сетевые запросы; значит, требование не выполняется приложением, и это оформляется как дефект.
4. Регрессия: `pytest -m "positive or negative"` — основные сценарии не должны сломаться.
