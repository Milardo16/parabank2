import allure
import pytest
from selenium import webdriver

from config.settings import settings
from utils import diagnostics
from utils.metrics import collector


# ---------- мультибраузерность: --browser chrome | firefox | chrome,firefox ----------
def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=settings.browser,
                     help="Браузер(ы) через запятую: chrome, firefox, edge")
    parser.addoption("--headless", action="store_true", default=settings.headless,
                     help="Запуск без графического окна")


def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        names = [b.strip().lower() for b in metafunc.config.getoption("--browser").split(",") if b.strip()]
        metafunc.parametrize("browser_name", names)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_sessionfinish(session, exitstatus):
    collector.save()


def _create_driver(name: str, headless: bool):
    if name == "chrome":
        opts = webdriver.ChromeOptions()
        opts.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={settings.window_width},{settings.window_height}")
        return webdriver.Chrome(options=opts)
    if name == "firefox":
        opts = webdriver.FirefoxOptions()
        if headless:
            opts.add_argument("-headless")
        driver = webdriver.Firefox(options=opts)
        driver.set_window_size(settings.window_width, settings.window_height)
        return driver
    if name == "edge":
        opts = webdriver.EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument(f"--window-size={settings.window_width},{settings.window_height}")
        return webdriver.Edge(options=opts)
    raise ValueError(f"Неподдерживаемый браузер: {name}")


# ---------- фикстуры ----------
@pytest.fixture
def driver(request, browser_name):
    """Получение и удаление драйвера. Неявное ожидание = 0, только явные ожидания."""
    drv = _create_driver(browser_name, request.config.getoption("--headless"))
    drv.implicitly_wait(0)
    yield drv
    failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    if failed:
        diagnostics.attach_all(drv)
    drv.quit()


@pytest.fixture
def url():
    """URL страницы регистрации."""
    return settings.base_url + settings.register_path


@pytest.fixture
def metrics(request, browser_name):
    collector.bind(request.node.name, browser_name)
    yield collector
    collector.attach_current_to_allure()
