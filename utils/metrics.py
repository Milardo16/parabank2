"""Сбор метрик по ходу теста: CSV + JSON + вложения в Allure."""
import csv
import json
import time
from contextlib import contextmanager
from datetime import datetime

import allure

from config.settings import settings


class MetricsCollector:
    FIELDS = ["timestamp", "browser", "test", "metric", "value_ms"]

    def __init__(self):
        self.rows: list[dict] = []
        self._test = ""
        self._browser = ""

    def bind(self, test: str, browser: str):
        self._test, self._browser = test, browser

    def add(self, metric: str, value_ms: float):
        self.rows.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "browser": self._browser,
            "test": self._test,
            "metric": metric,
            "value_ms": round(value_ms, 1),
        })

    @contextmanager
    def measure(self, metric: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.add(metric, (time.perf_counter() - start) * 1000)

    def for_current_test(self):
        return [r for r in self.rows if r["test"] == self._test and r["browser"] == self._browser]

    def attach_current_to_allure(self):
        rows = self.for_current_test()
        if not rows:
            return
        text = "\n".join(f"{r['metric']}: {r['value_ms']} ms" for r in rows)
        allure.attach(text, name="Метрики теста", attachment_type=allure.attachment_type.TEXT)
        allure.attach(json.dumps(rows, ensure_ascii=False, indent=2),
                      name="Метрики теста (JSON)", attachment_type=allure.attachment_type.JSON)

    def save(self):
        if not self.rows:
            return
        out = settings.reports_dir / "metrics"
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "metrics.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()
            writer.writerows(self.rows)
        with open(out / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(self.rows, f, ensure_ascii=False, indent=2)


collector = MetricsCollector()
