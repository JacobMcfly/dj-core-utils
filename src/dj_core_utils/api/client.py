import httpx
from django.conf import settings
from .exceptions import APIClientError


class AsyncAPIClient:
    def __init__(self, service_name):
        self.base_url = (
            f"http://{service_name}:8000/api"
            if settings.IS_MICROSERVICE
            else "http://localhost:8000/api"
        )

    async def request(self, method, endpoint, **kwargs):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    f"{self.base_url}/{endpoint}",
                    headers=self._get_headers(),
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise APIClientError(f"API Error: {e.response.text}")

    def _get_headers(self):
        headers = {}
        if settings.IS_MICROSERVICE:
            headers['Authorization'] = f'Service {settings.SERVICE_API_KEY}'
        return headers
