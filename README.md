# UI-тесты регистрации ParaBank

Автотесты формы регистрации https://parabank.parasoft.com/ на Python + Selenium + pytest + Allure.

## Структура

```
config/settings.py        параметры окружения (из .env)
pages/base_page.py        BasePage: низкоуровневые действия, явные ожидания
pages/registration_page.py RegistrationPage(BasePage): цепочка вызовов
tests/                    позитивный, негативные, новый кейс, безопасность
utils/                    данные, метрики, диагностика при падении
docs/CHANGE_CHAIN.md      требование → правка → проверка
pytest.ini                allure, маркеры
conftest.py               фикстуры driver / url / metrics, мультибраузерность
```

## Развёртывание

1. Установите Python 3.10+ и браузеры **Chrome** и/или **Firefox** (Edge — по желанию).
2. Создайте окружение и установите зависимости:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   source .venv/bin/activate       # Linux / macOS
   pip install -r requirements.txt
   ```
3. Драйверы (chromedriver / geckodriver) скачивать вручную **не нужно**: Selenium Manager (Selenium ≥ 4.6) подберёт и скачает их автоматически при первом запуске. Нужен доступ в интернет.
4. Настройте параметры: `copy .env.example .env` (Windows) / `cp .env.example .env` и отредактируйте значения.
5. Для просмотра отчёта установите Allure Commandline (https://allurereport.org/docs/install/), например `scoop install allure` или `brew install allure`.

## Параметры окружения (.env)

| Параметр | По умолчанию | Описание |
|---|---|---|
| BASE_URL | https://parabank.parasoft.com/parabank | адрес приложения |
| REGISTER_PATH | /register.htm | путь страницы регистрации |
| BROWSER | chrome | chrome / firefox / edge |
| HEADLESS | false | запуск без окна |
| EXPLICIT_TIMEOUT | 10 | таймаут явных ожиданий, с |
| WINDOW_WIDTH / WINDOW_HEIGHT | 1366 / 900 | размер окна |
| REPORTS_DIR | reports | папка отчётов и метрик |

Любой параметр можно переопределить переменной окружения.

## Запуск

```bash
pytest                                  # браузер из .env
pytest --browser firefox                # другой браузер
pytest --browser chrome,firefox         # оба браузера подряд
pytest --headless                       # без окна
pytest -m "positive or negative"        # по маркерам
pytest -m security                      # только проверки безопасности
pytest -m metrics                       # тесты с метриками
```

Маркеры: `smoke`, `positive`, `negative`, `security`, `metrics`, `regression`.

## Allure-отчёт

```bash
allure serve reports/allure-results
```

При падении теста в отчёт автоматически прикладываются: скриншот, логи браузера и сетевые запросы
(Chrome — из performance-лога; Firefox — через Resource Timing API, `get_log` в нём недоступен).

## Метрики

В ходе тестов собираются: `page_load_ms` (время загрузки страницы регистрации, Navigation Timing API),
`fill_form_ms`, `form_response_ms` (клик «Register» → ответ сервера), `registration_total_ms` и др.

* Файлы: `reports/metrics/metrics.csv` и `reports/metrics/metrics.json` (создаются в конце сессии).
* В Allure метрики каждого теста прикладываются как вложения «Метрики теста» (TEXT и JSON).

## Проверки безопасности (`tests/test_registration_security.py`)

HTTPS, маскирование паролей, метод POST, отсутствие пароля в URL, XSS-пейлоады (3 вида),
SQL-инъекции (3 вида), очень длинные значения, флаги cookie сессии и заголовки безопасности.
Две последние проверки помечены `xfail(strict=False)`: учебный сайт может их не выполнять — это фиксируется как замечание, а не как падение проекта.

## Новый тест-кейс

`tests/test_registration_new_case.py` — регистрация без номера телефона. Цепочка «требование → правка → проверка» описана в `docs/CHANGE_CHAIN.md`.
