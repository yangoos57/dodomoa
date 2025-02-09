import os

if os.getenv("DB_NAME"):
    url = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
else:
    url = "127.0.0.1"
    user = "root"


class Deployment:
    def __init__(self) -> None:
        self._db_dir = f"mysql+pymysql://{user}@{url}:3306"
        # db_dir = f"mysql+pymysql://{user}:{password}@{url}:3306"
        self._db_name = "dodomoa_db"
        self._columns = [
            "isbn13",
            "bookname",
            "authors",
            "publisher",
            "class_no",
            "reg_date",
            "bookImageURL",
        ]

    @property
    def db_dir(self):
        return self._db_dir

    @property
    def db_name(self):
        return self._db_name

    @property
    def api_auth_key(self):
        return self._api_auth_key

    @property
    def columns(self):
        return self._columns


class Test:
    def __init__(self) -> None:
        self._db_dir = f"mysql+pymysql://{user}:{url}:3306"
        self._db_name = "dodomoa_test"

    @property
    def db_dir(self):
        return self._db_dir

    @property
    def db_name(self):
        return self._db_name
