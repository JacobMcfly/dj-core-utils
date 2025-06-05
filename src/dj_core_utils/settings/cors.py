from typing import Any


def get_cors_settings(service_name: str) -> dict[str, Any]:
    return {
        'CORS_ALLOWED_ORIGINS': [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            f"http://{service_name}:8000",
        ],
        'CORS_URLS_REGEX': r'^/api/.*$',
        'CORS_ALLOW_CREDENTIALS': True,
    }
