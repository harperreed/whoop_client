from __future__ import annotations

import json
from typing import Any, List, Dict
from datetime import datetime, timedelta

from authlib.integrations.requests_client import OAuth2Session
from authlib.common.urls import extract_params

from .utils import WhoopConfig, format_dates

AUTH_URL = "https://api-7.whoop.com"
REQUEST_URL = "https://api.prod.whoop.com/developer"

def _auth_password_json(_client, _method, uri, headers, body):
    body = json.dumps(dict(extract_params(body)))
    headers["Content-Type"] = "application/json"
    return uri, headers, body

class WhoopClient:
    TOKEN_ENDPOINT_AUTH_METHOD = "password_json"

    def __init__(self, config: WhoopConfig, authenticate: bool = True):
        self._username = config.username
        self._password = config.password
        self.session = OAuth2Session(
            token_endpoint=f"{AUTH_URL}/oauth/token",
            token_endpoint_auth_method=self.TOKEN_ENDPOINT_AUTH_METHOD,
        )
        self.session.register_client_auth_method(
            (self.TOKEN_ENDPOINT_AUTH_METHOD, _auth_password_json)
        )
        self.user_id = ""
        if authenticate:
            self.authenticate()

    def __enter__(self) -> WhoopClient:
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def __str__(self) -> str:
        return f"WhoopClient({self.user_id if self.user_id else '<Unauthenticated>'})"

    def close(self) -> None:
        self.session.close()

    def authenticate(self, **kwargs) -> None:
        self.session.fetch_token(
            url=f"{AUTH_URL}/oauth/token",
            username=self._username,
            password=self._password,
            grant_type="password",
            **kwargs,
        )
        if not self.user_id:
            self.user_id = str(self.session.token.get("user", {}).get("id", ""))

    def is_authenticated(self) -> bool:
        return self.session.token is not None

    def _make_request(self, method: str, url_slug: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.session.request(
            method=method,
            url=f"{REQUEST_URL}/{url_slug}",
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def _make_paginated_request(self, method, url_slug, **kwargs) -> List[Dict[str, Any]]:
        params = kwargs.pop("params", {})
        response_data: List[Dict[str, Any]] = []

        while True:
            response = self._make_request(
                method=method,
                url_slug=url_slug,
                params=params,
                **kwargs,
            )
            response_data += response["records"]
            if next_token := response.get("next_token"):
                params["nextToken"] = next_token
            else:
                break

        return response_data

    def get_profile(self) -> Dict[str, Any]:
        return self._make_request(method="GET", url_slug="v1/user/profile/basic")

    def get_body_measurement(self) -> Dict[str, Any]:
        return self._make_request(method="GET", url_slug="v1/user/measurement/body")

    def get_cycle_collection(self, start_date: str | None = None, end_date: str | None = None) -> List[Dict[str, Any]]:
        start, end = format_dates(start_date, end_date)
        return self._make_paginated_request(
            method="GET",
            url_slug="v1/cycle",
            params={"start": start, "end": end, "limit": 25},
        )

    def get_recovery_collection(self, start_date: str | None = None, end_date: str | None = None) -> List[Dict[str, Any]]:
        start, end = format_dates(start_date, end_date)
        return self._make_paginated_request(
            method="GET",
            url_slug="v1/recovery",
            params={"start": start, "end": end, "limit": 25},
        )

    def get_sleep_collection(self, start_date: str | None = None, end_date: str | None = None) -> List[Dict[str, Any]]:
        start, end = format_dates(start_date, end_date)
        return self._make_paginated_request(
            method="GET",
            url_slug="v1/activity/sleep",
            params={"start": start, "end": end, "limit": 25},
        )

    def get_workout_collection(self, start_date: str | None = None, end_date: str | None = None) -> List[Dict[str, Any]]:
        start, end = format_dates(start_date, end_date)
        return self._make_paginated_request(
            method="GET",
            url_slug="v1/activity/workout",
            params={"start": start, "end": end, "limit": 25},
        )
