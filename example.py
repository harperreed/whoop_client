from whoop_client import WhoopClient
from whoop_client.utils import load_config
from datetime import datetime, timedelta
import pandas as pd

def main():
    # Load configuration
    config = load_config('./config.yaml')

    # Initialize the WhoopClient
    client = WhoopClient(config)

    print("Authentication successful!")
    print(f"User ID: {client.user_id}")

    # Get user profile
    profile = client.get_profile()
    print("\nUser Profile:")
    print(f"Name: {profile['first_name']} {profile['last_name']}")
    print(f"Email: {profile['email']}")

    # Get body measurements
    body = client.get_body_measurement()
    print("\nBody Measurements:")
    print(f"Height: {body['height_meter']:.2f} m")
    print(f"Weight: {body['weight_kilogram']:.2f} kg")
    print(f"Max Heart Rate: {body['max_heart_rate']} bpm")

    # Get cycles for the last 7 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"\nRetrieving cycles from {start_date} to {end_date}...")
    cycles = client.get_cycle_collection(start_date, end_date)
    print(f"Retrieved {len(cycles)} cycles")

    # Get recoveries for the last 7 days
    print(f"\nRetrieving recoveries from {start_date} to {end_date}...")
    recoveries = client.get_recovery_collection(start_date, end_date)
    print(f"Retrieved {len(recoveries)} recoveries")

    # Get sleep data for the last 7 days
    print(f"\nRetrieving sleep data from {start_date} to {end_date}...")
    sleep = client.get_sleep_collection(start_date, end_date)
    print(f"Retrieved {len(sleep)} sleep records")

    if sleep:
        df_sleep = pd.DataFrame(sleep)
        print("\nAverage sleep duration (hours):")
        avg_sleep_duration = (pd.to_datetime(df_sleep['end']) - pd.to_datetime(df_sleep['start'])).mean().total_seconds() / 3600
        print(f"{avg_sleep_duration:.2f}")

    # Get workouts for the last 7 days
    print(f"\nRetrieving workouts from {start_date} to {end_date}...")
    workouts = client.get_workout_collection(start_date, end_date)
    print(f"Retrieved {len(workouts)} workouts")

    if workouts:
        df_workouts = pd.DataFrame(workouts)
        print("\nAverage workout strain:")
        avg_strain = df_workouts['score'].apply(lambda x: x['strain']).mean()
        print(f"{avg_strain:.2f}")

if __name__ == "__main__":
    main()
