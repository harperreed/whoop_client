from typing import Union, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd

from .auth import WhoopAuth
from .data_retrieval import WhoopDataRetrieval
from .data_processing import WhoopDataProcessing
from .utils import load_config, WhoopConfig, validate_date_range

class WhoopClient:
    def __init__(self, config_path: Union[str, Path]):
        self.config = load_config(config_path)
        self.auth = WhoopAuth(self.config)
        self.data_retrieval = WhoopDataRetrieval(self.auth)
        self.data_processing = WhoopDataProcessing()

        self.current_datetime: datetime = datetime.utcnow()
        self.start_datetime: Optional[datetime] = None
        self.all_data: Optional[pd.DataFrame] = None
        self.all_activities: Optional[pd.DataFrame] = None
        self.all_sleep: Optional[pd.DataFrame] = None
        self.all_sleep_events: Optional[pd.DataFrame] = None

    def authenticate(self):
        self.auth.authenticate()
        self.start_datetime = self.auth.start_datetime

    def get_keydata_all(self) -> pd.DataFrame:
        if self.all_data is None:
            raw_data = self.data_retrieval.get_all_cycles()
            self.all_data = self.data_processing.process_keydata(raw_data)
        return self.all_data

    def get_activities_all(self) -> pd.DataFrame:
        if self.all_activities is None:
            raw_data = self.get_keydata_all()
            self.all_activities = self.data_processing.process_activities(raw_data)
        return self.all_activities

    def get_sleep_all(self) -> pd.DataFrame:
        if self.all_sleep is None:
            raw_data = self.get_keydata_all()
            sleep_ids = self.data_processing.extract_sleep_ids(raw_data)
            raw_sleep_data = self.data_retrieval.get_sleep_data(sleep_ids)
            self.all_sleep = self.data_processing.process_sleep(raw_sleep_data)
        return self.all_sleep

    def get_sleep_events_all(self) -> pd.DataFrame:
        if self.all_sleep_events is None:
            sleep_data = self.get_sleep_all()
            self.all_sleep_events = self.data_processing.process_sleep_events(sleep_data)
        return self.all_sleep_events

    def get_hr_all(self, as_dataframe: bool = False):
        raw_hr_data = self.data_retrieval.get_all_hr_data()
        return self.data_processing.process_hr_data(raw_hr_data, as_dataframe)

    def get_keydata_timeframe(self, start: str, end: Optional[str] = None) -> pd.DataFrame:
        end = end or datetime.now().strftime("%Y-%m-%d")
        start_date, end_date = validate_date_range(start, end)
        raw_data = self.data_retrieval.get_cycles_timeframe(start_date, end_date)
        return self.data_processing.process_keydata(raw_data)

    def get_activities_timeframe(self, start: str, end: Optional[str] = None) -> pd.DataFrame:
        keydata = self.get_keydata_timeframe(start, end)
        return self.data_processing.process_activities(keydata)

    def get_sleep_timeframe(self, start: str, end: Optional[str] = None) -> pd.DataFrame:
        keydata = self.get_keydata_timeframe(start, end)
        sleep_ids = self.data_processing.extract_sleep_ids(keydata)
        raw_sleep_data = self.data_retrieval.get_sleep_data(sleep_ids)
        return self.data_processing.process_sleep(raw_sleep_data)

    def get_sleep_events_timeframe(self, start: str, end: Optional[str] = None) -> pd.DataFrame:
        sleep_data = self.get_sleep_timeframe(start, end)
        return self.data_processing.process_sleep_events(sleep_data)

    def get_hr_timeframe(self, start: str, end: Optional[str] = None, as_dataframe: bool = False):
        end = end or datetime.now().strftime("%Y-%m-%d")
        start_date, end_date = validate_date_range(start, end)
        raw_hr_data = self.data_retrieval.get_hr_data_timeframe(start_date, end_date)
        return self.data_processing.process_hr_data(raw_hr_data, as_dataframe)

# You might want to include these to make the important classes and functions
# available when someone imports the package
from .auth import WhoopAuth
from .data_retrieval import WhoopDataRetrieval
from .data_processing import WhoopDataProcessing
from .utils import WhoopConfig, load_config, validate_date_range
