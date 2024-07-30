import requests
from typing import List, Dict
from datetime import datetime
from dateutil import relativedelta, rrule
from dateutil.rrule import WEEKLY

class WhoopDataRetrieval:
    def __init__(self, auth):
        self.auth = auth

    def _api_get(self, url: str, params: Dict = None) -> Dict:
        response = requests.get(url, headers=self.auth.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_all_cycles(self) -> List[Dict]:
        start_date = self.auth.start_datetime.replace(tzinfo=None)
        intervals = rrule.rrule(freq=WEEKLY, interval=1, until=datetime.utcnow(), dtstart=start_date)

        all_cycles = []
        for interval_start in intervals:
            interval_end = interval_start + relativedelta.relativedelta(weeks=1)
            cycles = self._get_cycle_data(interval_start, interval_end)
            all_cycles.extend(cycles)

        return all_cycles

    def _get_cycle_data(self, start: datetime, end: datetime) -> List[Dict]:
        url = f'https://api-7.whoop.com/users/{self.auth.whoop_id}/cycles'
        params = {
            'start': start.isoformat() + 'Z',
            'end': end.isoformat() + 'Z'
        }
        return self._api_get(url, params=params)

    def get_sleep_data(self, sleep_ids: List[int]) -> List[Dict]:
        return [self._get_sleep_main(s) for s in sleep_ids]

    def _get_sleep_main(self, sleep_id: int) -> Dict:
        url = f'https://api-7.whoop.com/users/{self.auth.whoop_id}/sleeps/{sleep_id}'
        return self._api_get(url)

    def get_all_hr_data(self) -> List[Dict]:
        start_date = self.auth.start_datetime.replace(tzinfo=None)
        intervals = rrule.rrule(freq=WEEKLY, interval=1, until=datetime.utcnow(), dtstart=start_date)

        all_hr_data = []
        for interval_start in intervals:
            interval_end = interval_start + relativedelta.relativedelta(weeks=1)
            hr_data = self._get_hr_data(interval_start, interval_end)
            all_hr_data.extend(hr_data)

        return all_hr_data

    def _get_hr_data(self, start: datetime, end: datetime) -> List[Dict]:
        url = f'https://api-7.whoop.com/users/{self.auth.whoop_id}/metrics/heart_rate'
        params = {
            'start': start.isoformat() + 'Z',
            'end': end.isoformat() + 'Z',
            'order': 't',
            'step': 6
        }
        return self._api_get(url, params=params)['values']
