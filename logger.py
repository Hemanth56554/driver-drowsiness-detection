import csv
import os
from datetime import datetime

LOG_FILE = "events.csv"


def log_event(event_type, ear, mar):
    """Add one row to events.csv (creates the file with a header the first time)."""
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["date", "time", "event", "ear", "mar"])
        now = datetime.now()
        writer.writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            event_type,
            f"{ear:.2f}",
            f"{mar:.2f}",
        ])