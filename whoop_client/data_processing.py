import pandas as pd
import numpy as np
from typing import List, Dict, Union
from datetime import datetime

class WhoopDataProcessing:
    def process_keydata(self, raw_data: List[Dict]) -> pd.DataFrame:
        df = pd.json_normalize(raw_data)
        df['days'] = df['days'].map(lambda d: d[0])
        df.rename(columns={"days": 'day'}, inplace=True)
        self._process_sleep_data(df)
        return df.drop_duplicates(subset=['day', 'sleep.id'])

    def _process_sleep_data(self, df: pd.DataFrame) -> None:
        sleep_cols = [
            'qualityDuration', 'needBreakdown.baseline', 'needBreakdown.debt',
            'needBreakdown.naps', 'needBreakdown.strain', 'needBreakdown.total'
        ]
        for col in sleep_cols:
            df[f'sleep.{col}'] = df[f'sleep.{col}'].astype(float).apply(lambda x: np.nan if np.isnan(x) else x / 60000)

        df['nap_duration'] = df['sleep.naps'].apply(self._calculate_nap_duration)
        df.drop(['sleep.naps'], axis=1, inplace=True)

    @staticmethod
    def _calculate_nap_duration(naps: List[Dict]) -> float:
        if not naps:
            return 0
        return sum(nap['qualityDuration'] for nap in naps if nap['qualityDuration'] is not None) / 60000

    def process_activities(self, data: pd.DataFrame) -> pd.DataFrame:
        act_data = pd.json_normalize(data[data['strain.workouts'].apply(len) > 0]['strain.workouts'].apply(lambda x: x[0]))
        act_data[['during.upper', 'during.lower']] = act_data[['during.upper', 'during.lower']].apply(pd.to_datetime)
        act_data['total_minutes'] = (act_data['during.upper'] - act_data['during.lower']).dt.total_seconds() / 60.0

        for z in range(6):
            act_data[f'zone{z+1}_minutes'] = act_data['zones'].apply(lambda x: x[z] / 60000.)

        act_data['day'] = act_data['during.lower'].dt.strftime('%Y-%m-%d')
        act_data.drop(['zones', 'during.bounds'], axis=1, inplace=True)
        return act_data.drop_duplicates()

    def process_sleep(self, raw_sleep_data: List[Dict]) -> pd.DataFrame:
        df = pd.json_normalize(raw_sleep_data)
        self._process_sleep_metrics(df)
        df.drop(['during.bounds', 'events'], axis=1, inplace=True)
        return df

    def _process_sleep_metrics(self, df: pd.DataFrame) -> None:
        sleep_metrics = [
            'qualityDuration', 'latency', 'debtPre', 'debtPost', 'needFromStrain',
            'sleepNeed', 'habitualSleepNeed', 'timeInBed', 'lightSleepDuration',
            'slowWaveSleepDuration', 'remSleepDuration', 'wakeDuration', 'arousalTime',
            'noDataDuration', 'creditFromNaps', 'projectedSleep'
        ]
        for col in sleep_metrics:
            df[col] = df[col].astype(float).apply(lambda x: np.nan if np.isnan(x) else x / 60000)

    def process_sleep_events(self, sleep_data: pd.DataFrame) -> pd.DataFrame:
        events_data = []
        for _, row in sleep_data.iterrows():
            events = pd.json_normalize(row['events'])
            events['id'] = row['id']
            events_data.append(events)

        df = pd.concat(events_data, ignore_index=True)
        df['during.lower'] = pd.to_datetime(df['during.lower'])
        df['during.upper'] = pd.to_datetime(df['during.upper'])
        df.drop(['during.bounds'], axis=1, inplace=True)
        df['total_minutes'] = (df['during.upper'] - df['during.lower']).dt.total_seconds() / 60.0
        return df

    def process_hr_data(self, hr_vals: List[Dict], as_dataframe: bool = False) -> Union[List[List], pd.DataFrame]:
        hr_list = [
            (
                datetime.utcfromtimestamp(h['time'] / 1e3).date(),
                datetime.utcfromtimestamp(h['time'] / 1e3).time(),
                h['data']
            )
            for h in hr_vals
        ]

        if as_dataframe:
            return pd.DataFrame(hr_list, columns=['date', 'time', 'hr'])
        return hr_list

    def extract_sleep_ids(self, data: pd.DataFrame) -> List[int]:
        return [int(x) for x in data['sleep.id'].dropna().unique()]
