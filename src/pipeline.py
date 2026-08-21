import logging

import pandas as pd
import requests

from config import (
    API_URL,
    CLEAN_FILE,
    LOG_FILE,
    OUTPUT_DIR,
    RAW_FILE,
    REQUEST_TIMEOUT,
)


def setup_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def fetch_users():
    response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    users = response.json()
    logging.info("Fetched %d records", len(users))
    return users


def transform_users(users):
    data = [
        {
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"],
            "city": user["address"]["city"],
            "company": user["company"]["name"],
        }
        for user in users
    ]

    return pd.DataFrame(data)


def clean_users(df):
    before_cleaning = len(df)

    df = df.drop_duplicates()
    duplicates_removed = before_cleaning - len(df)

    before_missing_check = len(df)
    df = df.dropna(subset=["name", "email"])
    missing_removed = before_missing_check - len(df)

    text_columns = ["name", "username", "email", "city", "company"]
    for column in text_columns:
        df[column] = df[column].str.strip()

    df["email"] = df["email"].str.lower()

    invalid_emails = ~df["email"].str.contains(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        regex=True,
        na=False,
    )

    invalid_removed = invalid_emails.sum()
    df = df[~invalid_emails].copy()

    if df.empty:
        raise ValueError("No valid records remaining after validation.")

    logging.info("Duplicates removed: %d", duplicates_removed)
    logging.info("Missing records removed: %d", missing_removed)
    logging.info("Invalid emails removed: %d", invalid_removed)
    logging.info("Final records: %d", len(df))

    return df


def main():
    setup_logging()

    try:
        logging.info("Pipeline started")

        users = fetch_users()
        raw_df = transform_users(users)

        raw_df.to_csv(RAW_FILE, index=False)
        logging.info("Raw data saved to %s", RAW_FILE)

        clean_df = clean_users(raw_df)
        clean_df.to_csv(CLEAN_FILE, index=False)

        logging.info("Pipeline completed successfully")
        print("Pipeline completed successfully!")
        print(f"Records: {len(clean_df)}")
        print(f"Clean file: {CLEAN_FILE}")

    except requests.RequestException as error:
        logging.error("API request failed: %s", error)
        print("ERROR: Could not fetch data.")

    except Exception as error:
        logging.exception("Pipeline failed: %s", error)
        print("ERROR: Pipeline failed.")


if __name__ == "__main__":
    main()