"""Диагностика при падении теста: скриншот, логи браузера, сетевые запросы."""
import json

import allure


def attach_screenshot(driver):
    allure.attach(driver.get_screenshot_as_png(), name="Скриншот при падении",
                  attachment_type=allure.attachment_type.PNG)


def attach_browser_logs(driver):
    try:
        logs = driver.get_log("browser")
        text = "\n".join(f"[{e['level']}] {e['message']}" for e in logs) or "Логи консоли пусты"
    except Exception:
        text = "Браузер не отдаёт логи через get_log (характерно для Firefox)"
    allure.attach(text, name="Логи браузера", attachment_type=allure.attachment_type.TEXT)


def _network_from_perf_log(driver):
    result = []
    for entry in driver.get_log("performance"):
        msg = json.loads(entry["message"])["message"]
        if msg["method"] == "Network.responseReceived":
            r = msg["params"]["response"]
            result.append({"url": r["url"], "status": r["status"], "type": msg["params"].get("type")})
    return result


def _network_from_js(driver):
    return driver.execute_script(
        "return performance.getEntriesByType('resource').map(e => ({url: e.name,"
        " type: e.initiatorType, duration_ms: Math.round(e.duration)}));")


def attach_network(driver):
    try:
        data = _network_from_perf_log(driver)
    except Exception:
        data = _network_from_js(driver)
    allure.attach(json.dumps(data, ensure_ascii=False, indent=2), name="Сетевые запросы",
                  attachment_type=allure.attachment_type.JSON)


def attach_all(driver):
    for func in (attach_screenshot, attach_browser_logs, attach_network):
        try:
            func(driver)
        except Exception as exc:  # диагностика не должна ломать teardown
            allure.attach(str(exc), name=f"Ошибка {func.__name__}", attachment_type=allure.attachment_type.TEXT)
