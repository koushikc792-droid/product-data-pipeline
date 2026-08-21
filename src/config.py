from pathlib import Path

API_URL = "https://jsonplaceholder.typicode.com/users"

OUTPUT_DIR = Path("output")

RAW_FILE = OUTPUT_DIR / "users_raw.csv"
CLEAN_FILE = OUTPUT_DIR / "users_cleaned.csv"
LOG_FILE = OUTPUT_DIR / "pipeline.log"

REQUEST_TIMEOUT = 10