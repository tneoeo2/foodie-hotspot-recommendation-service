import csv

from accounts.models import Location
from utils.custom_logger import CustomLogger

logger = CustomLogger("INFO").get_logger()


def load_to_db():
    with open("./utils/location/location_data.csv", "r", encoding="utf-8-sig") as f:
        csv_to_list = list(csv.DictReader(f))

        for i, row in enumerate(csv_to_list):
            logger.info(f"location check: {i+1}/{len(csv_to_list)}")
            temp = Location(**row)
            temp.custom_save()

            
