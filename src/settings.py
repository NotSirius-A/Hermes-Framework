import scrapers, storages, mailers
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

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