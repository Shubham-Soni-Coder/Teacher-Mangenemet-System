from app.utils.json_loader import load_json
from app.utils.seeder import DataBaseCreate
import time

if __name__ == "__main__":
    data = load_json()
    start = time.time()
    creater = DataBaseCreate()
    creater.Create()
    print(f"Time is {start-time.time()}")
