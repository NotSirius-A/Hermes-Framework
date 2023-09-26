import scrapers, storages, mailers
from pathlib import Path
import logging, sys

BASE_DIR = Path(__file__).resolve().parent



logging.basicConfig(
                handlers=[
                    logging.FileHandler("logs.log"),
                    logging.StreamHandler(sys.stdout)
                ],
                format='[%(asctime)s] %(name)s : %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                level=logging.INFO
)




NOTIFY = True

MAX_ARTICLES = 100

scraper_objs = [
    #scrapers.MyScraper(url="https://url"),
]

#storage_obj = storages.MyStorage(BASE_DIR)

# Importing credentials - example simple implementation
# with open(Path(BASE_DIR, "crendtials.txt"), 'r') as f:
#     email = f.readline().strip()
#     password = f.readline().strip()


# notifier_objs = [
#     mailers.MyMailer(
#         receivers_path=Path(BASE_DIR, "MyMailer_receivers.json"),
#         smtp_port=587,
#         smtp_server="yoursmtp.com",
#         bot_email=email,
#         bot_password=password,
#     ),
# ]