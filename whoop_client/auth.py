import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser
from typing import Optional
import requests
from cryptography.fernet import Fernet
from .utils import WhoopConfig

class WhoopAuth:
    def __init__(self, config: WhoopConfig):
        self.config = config
        self.auth_code: str = ""
        self.whoop_id: str = ""
        self.start_datetime: datetime = datetime.min
        self.auth_expiration: Optional[datetime] = None
        self.token_lifetime: timedelta = timedelta(hours=24)  # Adjust based on actual token lifetime
        self.cache_file = Path.home() / '.whoop_auth_cache'
        self.encryption_key = self._get_or_create_key()

    def _get_or_create_key(self) -> bytes:
        key_file = Path.home() / '.whoop_auth_key'
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            return key

    def authenticate(self) -> None:
        if self._load_cached_auth():
            print("Using cached authentication")
            return

        headers = {
            "username": self.config.username,
            "password": self.config.password,
            "grant_type": "password",
            "issueRefresh": False
        }
        response = requests.post("https://api-7.whoop.com/oauth/token", json=headers)
        response.raise_for_status()

        content = response.json()
        self.whoop_id = content['user']['id']
        self.auth_code = f"bearer {content['access_token']}"
        self.start_datetime = parser.isoparse(content['user']['profile']['createdAt'])
        self.auth_expiration = datetime.now() + self.token_lifetime

        self._save_auth_to_cache()
        print("Authentication successful")

    def get_headers(self) -> dict:
        if not self._is_auth_valid():
            self.authenticate()
        return {'authorization': self.auth_code}

    def _is_auth_valid(self) -> bool:
        if not self.auth_code or not self.auth_expiration:
            return False
        return datetime.now() < self.auth_expiration

    def _save_auth_to_cache(self) -> None:
        data = {
            'auth_code': self.auth_code,
            'whoop_id': self.whoop_id,
            'start_datetime': self.start_datetime.isoformat(),
            'auth_expiration': self.auth_expiration.isoformat()
        }
        encrypted_data = Fernet(self.encryption_key).encrypt(json.dumps(data).encode())
        self.cache_file.write_bytes(encrypted_data)

    def _load_cached_auth(self) -> bool:
        if not self.cache_file.exists():
            return False

        encrypted_data = self.cache_file.read_bytes()
        try:
            data = json.loads(Fernet(self.encryption_key).decrypt(encrypted_data))
            self.auth_code = data['auth_code']
            self.whoop_id = data['whoop_id']
            self.start_datetime = parser.isoparse(data['start_datetime'])
            self.auth_expiration = parser.isoparse(data['auth_expiration'])

            if self._is_auth_valid():
                return True
            else:
                # Clear invalid cache
                self.cache_file.unlink(missing_ok=True)
                return False
        except Exception:
            # If there's any error in decrypting or parsing, consider the cache invalid
            self.cache_file.unlink(missing_ok=True)
            return False
