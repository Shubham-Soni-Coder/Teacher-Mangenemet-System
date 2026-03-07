import json
import os


def load_json(filename: str = "data.json"):

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found")

    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
