from typing import Any

TOKEN_PACKAGES = {
    "start": {"tokens": 20, "stars": 50, "label": "Старт"},
    "basic": {"tokens": 100, "stars": 200, "label": "Базовый"},
    "pro": {"tokens": 500, "stars": 800, "label": "Про"},
    "business": {"tokens": 1000, "stars": 1400, "label": "Бизнес"},
}


def get_packages() -> list[dict[str, Any]]:
    return [{"id": k, **v} for k, v in TOKEN_PACKAGES.items()]


def get_package(package_id: str) -> dict[str, Any] | None:
    pkg = TOKEN_PACKAGES.get(package_id)
    if not pkg:
        return None
    return {"id": package_id, **pkg}
